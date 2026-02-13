from langchain_core.prompts import ChatPromptTemplate



def query_analyzer_prompt():
    system = """You are an expert at converting user questions into database queries. \
    You have access to a database of Northwestern University professors and labs information. \
    Given a question, return a database query optimized to retrieve the most relevant results.

    If there are acronyms or words you are not familiar with, do not try to rephrase them."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    return prompt

def query_translation_prompt():
    template = """You are an AI language model assistant. Your task is to generate five 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_queries = ChatPromptTemplate.from_template(template)

    return prompt_queries

def query_router_prompt():
    system = """You are an expert at routing a user's question to the most relevant pipeline.
    1. 'academic_search': For questions about Northwestern University's McCormick School of Engineering, 
    including specific professors, labs, departments, or finding local experts in a field.
    2. 'general_research': For general scientific knowledge, terminology explanations, or 
    research concepts that are independent of any specific institution.

    If the user mentions a name or a lab that sounds like it belongs to an institution, default to 'academic_search'."""
    router_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )

    return router_prompt

def rag_chain_prompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_message}"),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    return prompt
