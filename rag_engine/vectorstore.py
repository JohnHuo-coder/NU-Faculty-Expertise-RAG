from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from process_documents.prepare_professors_info import prepare_professors_info
from process_documents.prepare_labs_info import prepare_labs_info

def build_vector_store():
    professors_info_filepath = "crawl_NU/professors_info.json"
    labs_info_filepath = "crawl_NU/labs_info.json"

    professors_docs = prepare_professors_info(professors_info_filepath)
    labs_docs = prepare_labs_info(labs_info_filepath)


    prof_text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = 1000,
        chunk_overlap = 100
    )
    prof_splits = prof_text_splitter.split_documents(professors_docs)

    lab_text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = 300,   
        chunk_overlap = 30  
    )
    lab_splits = lab_text_splitter.split_documents(labs_docs)

    all_documents = prof_splits + lab_splits

    embeddings = OpenAIEmbeddings()
    # vector_db = QdrantVectorStore.from_documents(
    #     documents,
    #     embeddings,
    #     path="./qdrant_db",  
    #     collection_name="nu_professors",
    # )

    vector_db = QdrantVectorStore.from_documents(
        all_documents,
        embeddings,
        location=":memory:", 
        collection_name="nu_research", 
    )

    return vector_db