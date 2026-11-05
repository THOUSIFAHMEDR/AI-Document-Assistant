from app.services.pdf_processor import extract_text_from_pdf
from app.services.text_chunker import chunk_documents
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import FaissVectorStore


def process_document(pdf_bytes: bytes):

    # Step 1: Extract PDF text
    pages = extract_text_from_pdf(pdf_bytes)

    # Step 2: Divide text into chunks
    chunks = chunk_documents(
        pages,
        chunk_size=500,
        overlap=100
    )

    if not chunks:
        raise ValueError("No text chunks generated.")

    # Step 3: Generate embeddings
    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts)

    # Step 4: Store embeddings in FAISS
    store = FaissVectorStore()

    store.add_embeddings(
        embeddings,
        chunks
    )

    return store, chunks