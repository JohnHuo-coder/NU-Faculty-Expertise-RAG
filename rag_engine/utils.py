from langchain_core.load import dumps, loads

def get_unique_union(documents: list[list]):
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))
    # Return
    return [loads(doc) for doc in unique_docs]

def format_docs(docs):
    return "\n\n".join(
        f"Name: {d.metadata.get('name')}\n"
        f"Dept: {d.metadata.get('department')}\n"
        f"Contact: {d.metadata.get('contact')}\n"
        f"Position: {d.metadata.get('position', '')}\n"
        f"Website: {d.metadata.get('website', '')}\n"
        f"Related Content: {d.page_content}"
        for d in docs
    )