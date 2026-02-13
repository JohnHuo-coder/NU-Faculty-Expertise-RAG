from rag_engine.vectorstore import build_vector_store
def build_retriever():
    vector_db = build_vector_store()
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    return retriever