import json
from langchain_core.documents import Document

def clean_item(item):
    cleaned_item = {}
    for key, value in item.items():
        if not value: continue
        k = key.lower().strip()
        if "research" in k:
            target_key = "research"
        elif any(x in k for x in ["publications", "books", "project", "patents"]):
            target_key = "publications"
        elif any(x in k for x in ["courses", "lectures"]):
            target_key = "courses"
        elif any(x in k for x in ["teaching", "students", "classroom"]):
            target_key = "teaching"
        elif "experience" in k:
            target_key = "experience"
        elif "website" in k:
            target_key = "website"
        elif "news" in k:
            target_key = "news"
        elif k in ["positions", "position"]:
            target_key = "position"
        else:
            target_key = k
        if target_key in cleaned_item:
            if value not in cleaned_item[target_key]:
                cleaned_item[target_key] += "\n" + value
        else:
            cleaned_item[target_key] = value
    return cleaned_item

def prepare_professors_info(doc_path):

    with open(doc_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # reformatting the keys and make up content to store
    documents = []
    for item in raw_data:
        cleaned_item = clean_item(item)
        search_parts = [
            f"Professor {cleaned_item.get('name')} is a {cleaned_item.get('position')} from {cleaned_item.get('departments')}",
            f"Research & Expertise: {cleaned_item.get('research', '')}",
            f"Publications & Works: {cleaned_item.get('publications', '')}",
            f"Biography: {cleaned_item.get('biography', '')}",
            f"Experience: {cleaned_item.get('experience', '')}",
            f"Courses & Teaching: {cleaned_item.get('courses', '')} {cleaned_item.get('teaching', '')}"
        ]
        full_search_text = "\n".join([p for p in search_parts if len(p) > 25])
        metadata = {
            "name": cleaned_item.get("name"),
            "position": cleaned_item.get("position"),
            "department": cleaned_item.get("departments"),
            "contact": cleaned_item.get("contact"),
            "website": cleaned_item.get("website"),
            "source_type": "professor"
        }
        if full_search_text.strip():
            doc = Document(page_content=full_search_text, metadata=metadata)
            documents.append(doc)

    return documents
