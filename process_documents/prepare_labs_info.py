import json
from langchain_core.documents import Document

def prepare_labs_info(doc_path):

    with open(doc_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # reformatting the keys and make up content to store
    documents = []
    for item in raw_data:

        search_parts = [
            f"Lab Name: {item.get('name', '')}",
            f"Lab Description: {item.get('description', '')}"
        ]
        full_search_text = "\n".join([p for p in search_parts])
        metadata = {
            "leader": item.get("leader"),
            "department": "Computer Science"
        }
        if full_search_text.strip():
            doc = Document(page_content=full_search_text, metadata=metadata)
            documents.append(doc)

    return documents