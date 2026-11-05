from typing import List, Dict


def chunk_documents(
    pages: List[Dict],
    chunk_size: int = 500,
    overlap: int = 100
) -> List[Dict]:

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []

    for page in pages:
        text = page["text"].strip()
        page_number = page["page_number"]

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page_number": page_number,
                    "text": chunk_text
                })

            start += chunk_size - overlap

    return chunks