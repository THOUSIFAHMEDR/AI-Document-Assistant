import json
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.document_service import process_document
from app.services.qa_service import answer_question
from app.services.vector_store import FaissVectorStore


app = FastAPI(
    title="AI Document Assistant",
    description="Upload PDFs and ask questions using AI.",
    version="1.0.0"
)

# Temporary in-memory document storage
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

VECTORSTORE_DIR = BASE_DIR / "vectorstore"
UPLOAD_DIR = BASE_DIR / "uploads"

VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

document_stores = {}
def load_saved_documents():
    """Load previously saved FAISS indexes when the server starts."""

    for document_dir in VECTORSTORE_DIR.iterdir():

        if not document_dir.is_dir():
            continue

        try:
            store = FaissVectorStore.load(str(document_dir))

            document_id = document_dir.name
            document_stores[document_id] = store

            print(f"Loaded saved document: {document_id}")

        except Exception:
            logging.exception(
                "Could not load document from %s",
                document_dir
            )


load_saved_documents()


class QuestionRequest(BaseModel):
    document_id: str
    question: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AI Document Assistant API is running."
    }


@app.post("/upload")
def upload_document(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    pdf_bytes = file.file.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )

    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="PDF size must not exceed 20 MB."
        )

    try:
        store, chunks = process_document(pdf_bytes)

        document_id = str(uuid4())

        # Save FAISS index and chunk metadata
        document_storage_path = VECTORSTORE_DIR / document_id
        store.save(str(document_storage_path))

# Save the original PDF
        pdf_storage_path = UPLOAD_DIR / f"{document_id}.pdf"
        pdf_storage_path.write_bytes(pdf_bytes)

# Keep the store available for immediate questions
        document_stores[document_id] = store

        return {
            "message": "Document processed successfully.",
            "document_id": document_id,
            "total_chunks": len(chunks)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        logging.exception("DOCUMENT PROCESSING ERROR")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check server logs."
        )


@app.post("/ask")
def ask_question(request: QuestionRequest):

    store = document_stores.get(request.document_id)

    if store is None:
        doc_dir = VECTORSTORE_DIR / request.document_id
        if doc_dir.exists() and (doc_dir / "document.index").exists():
            try:
                store = FaissVectorStore.load(str(doc_dir))
                document_stores[request.document_id] = store
            except Exception:
                pass

    if store is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload the PDF again."
        )

    try:
        result = answer_question(
            store,
            request.question
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Question processing failed. Check server logs."
        )


@app.get("/documents")
def list_documents():
    """List all saved documents and their metadata."""
    documents = []

    for doc_dir in VECTORSTORE_DIR.iterdir():
        if not doc_dir.is_dir():
            continue

        doc_id = doc_dir.name
        pdf_path = UPLOAD_DIR / f"{doc_id}.pdf"
        meta_path = doc_dir / "metadata.json"

        total_chunks = 0
        total_pages = 0
        title = f"Document-{doc_id[:8]}"

        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    chunks_meta = json.load(f)
                    total_chunks = len(chunks_meta)
                    if chunks_meta:
                        total_pages = max(c.get("page_number", 1) for c in chunks_meta)
            except Exception:
                pass

        file_size = 0
        created_at = doc_dir.stat().st_mtime

        if pdf_path.exists():
            try:
                file_size = pdf_path.stat().st_size
                created_at = pdf_path.stat().st_mtime
                import pymupdf as fitz
                pdf_doc = fitz.open(str(pdf_path))
                if len(pdf_doc) > total_pages:
                    total_pages = len(pdf_doc)
                pdf_title = (pdf_doc.metadata.get("title") or "").strip()
                if pdf_title:
                    title = pdf_title
                pdf_doc.close()
            except Exception:
                pass

        documents.append({
            "document_id": doc_id,
            "title": title,
            "filename": f"{title}.pdf" if not title.lower().endswith(".pdf") else title,
            "total_chunks": total_chunks,
            "total_pages": total_pages,
            "file_size": file_size,
            "created_at": created_at,
            "status": "ready"
        })

    documents.sort(key=lambda d: d["created_at"], reverse=True)
    return {"documents": documents}


@app.get("/documents/{document_id}/pdf")
def get_document_pdf(document_id: str):
    """Retrieve the original PDF file for a document."""
    pdf_path = UPLOAD_DIR / f"{document_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF document not found."
        )
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{document_id}.pdf"
    )
