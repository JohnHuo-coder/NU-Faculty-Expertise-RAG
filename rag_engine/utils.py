from langchain_core.load import dumps, loads

# def get_unique_union(documents: list[list]):
#     """ Unique union of retrieved docs """
#     # Flatten list of lists, and convert each Document to string
#     flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
#     # Get unique documents
#     unique_docs = list(set(flattened_docs))
#     # Return
#     return [loads(doc) for doc in unique_docs]

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

def reciprocal_rank_fusion(results: list[list], k = 60, return_scores=False):
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            fused_scores[doc_str] += 1 / (k + rank)

    sorted_items = sorted(fused_scores.items(),key=lambda item: item[1],reverse=True)
    
    if return_scores:
        return [(loads(doc_str), score) for doc_str, score in sorted_items]
    else:
        return [loads(doc_str) for doc_str, _ in sorted_items]
            