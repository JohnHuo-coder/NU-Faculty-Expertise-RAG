from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.load import dumps, loads
from qdrant_client import models

from rag_engine.prompts import query_router_prompt, query_analyzer_prompt, query_translation_prompt, rag_chain_prompt
from rag_engine.schemas import RouteQuery, ProfandLabSearch
from rag_engine.utils import reciprocal_rank_fusion, format_docs

system_content_choice_1 = """You are an expert academic research assistant specializing in the Northwestern University McCormick School of Engineering faculty and research laboratories.

    Your goal is to provide comprehensive information about professors and their associated labs based on the provided context.

    ### Guidelines:
    1. **Entity Linking**: Always identify the connection between professors and labs. If the context mentions a professor leads a specific lab (e.g., 'AquaLab'), ensure both are mentioned together.
    2. **Contextual Retrieval**:
        - **For Professor Queries**: Provide their name, department, position, and the primary research areas they focus on.
        - **For Lab Queries**: Provide the lab name, the faculty director (Professor), and the specific projects or technologies the lab is developing.
    3. **Technical Mapping**: If a user's technical term (e.g., 'LLM') doesn't have a literal match, bridge the gap by referring to broader context terms like 'Natural Language Processing', 'Machine Learning', or 'Artificial Intelligence'.
    4. **Structured Response**:
        - Mention the **Department** and **Contact/Website** info if available in the context.
        - If multiple professors/labs are relevant, list them clearly with brief descriptions of their distinct focus.
    5. **Strict Grounding & Integrity**: 
        - Only answer based on the **Context** provided. 
        - If the context lacks a specific professor or lab for a topic, state: "Based on the current Northwestern database, I couldn't find a specific professor or lab researching [Topic]." 
        - Do not hallucinate names or affiliations not present in the context.
    """

system_content_choice_2 = """ You are a professional research scientist. 
Your expertise is in general concepts. If the user mentions specific universities, professors, or faculty, do not try to search for local data; instead, explain the scientific concepts behind their inquiry
You are great at answering general research-related question, explain terminologies and concepts, and help plan experiments
You will answer all questions in a concise and easy to understand manner, explain in detail if the user asks.
When you don't know the answer to a question you admit that you don't know.
"""

def choose_prompt(result):
    if "academic_search" in result.target.lower():
        return system_content_choice_1
    else:
        return system_content_choice_2
        
def get_system_message_chain(llm):

    structured_llm = llm.with_structured_output(RouteQuery)

    router_prompt = query_router_prompt()

    selected_prompt = router_prompt | structured_llm | RunnableLambda(choose_prompt) 

    return selected_prompt

def query_logic(structured_obj, generated_queries, retriever):
    query = structured_obj.query
    queries = generated_queries.invoke({"question": query})
    q_filter = None
    filters = []
    if structured_obj.source_type:
        filters.append(models.FieldCondition(key="source_type", match=models.MatchValue(value = structured_obj.source_type)))
    if structured_obj.professor_name: 
        filters.append(models.FieldCondition(key="name", match=models.MatchValue(value = structured_obj.professor_name)))
    if structured_obj.position: 
        filters.append(models.FieldCondition(key="position", match=models.MatchValue(value = structured_obj.position)))
    if structured_obj.lab_name: 
        filters.append(models.FieldCondition(key="name", match=models.MatchValue(value = structured_obj.lab_name)))
    if structured_obj.lab_leader: 
        filters.append(models.FieldCondition(key="leader", match=models.MatchValue(value = structured_obj.lab_leader)))
    if structured_obj.department: 
        filters.append(models.FieldCondition(key="department", match=models.MatchValue(value = structured_obj.department)))
    if filters:
        q_filter = models.Filter(must=filters)
    all_docs = []
    for q in queries:
        docs = retriever.invoke(q, config={"configurable": {"search_kwargs": {"filter": q_filter}}})
        all_docs.append(docs)
    return reciprocal_rank_fusion(all_docs)

def get_retrieval_chain(llm, retriever):
    # Query structuring for metadata filters
    q_analyzer_prompt = query_analyzer_prompt()
    structured_llm = llm.with_structured_output(ProfandLabSearch)
    query_analyzer = q_analyzer_prompt | structured_llm


    # query translation
    prompt_queries = query_translation_prompt()
    generated_queries = prompt_queries | llm | StrOutputParser() | (lambda x: x.split('\n'))
    def bound_query_logic(structured_obj):
        return query_logic(structured_obj, generated_queries, retriever)

    retrieval_chain = query_analyzer | RunnableLambda(bound_query_logic) | RunnableLambda(format_docs)

    return retrieval_chain

def get_rag_chain(llm, retriever):
    system_message_chain = get_system_message_chain(llm)
    retrieval_chain = get_retrieval_chain(llm, retriever)
    prompt = rag_chain_prompt()

    def get_question(input_dict):
        return input_dict.get("question", "")

    def get_chat_history(input_dict):
        return input_dict.get("chat_history", "")

    rag_chain = (
        {
            "system_message": system_message_chain,
            "context": retrieval_chain,
            "question": RunnableLambda(get_question),
            "chat_history": RunnableLambda(get_chat_history),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain