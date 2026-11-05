import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pymupdf as fitz
from fastapi.testclient import TestClient
from app.main import app


def test_full_rag_pipeline():
    client = TestClient(app)

    print("\n--- 1. Testing GET /health ---")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print("Health response:", health_data)
    assert health_data["status"] == "healthy"

    print("\n--- 2. Testing GET /documents ---")
    res = client.get("/documents")
    assert res.status_code == 200, f"List documents failed: {res.text}"
    docs = res.json().get("documents", [])
    print(f"Found {len(docs)} documents in persistent library.")
    for d in docs:
        print(f"  - Document: {d['title']} ({d['document_id']}) | Pages: {d['total_pages']} | Chunks: {d['total_chunks']}")

    print("\n--- 3. Testing POST /upload with a clean 2-page PDF ---")
    # Generate test PDF in memory
    pdf = fitz.open()
    page1 = pdf.new_page()
    page1.insert_text(
        (50, 70),
        "AI Research Report 2026\n"
        "Project: Autonomous Agent Architecture\n"
        "Executive Summary: We evaluated the RAG retrieval pipeline with FAISS and Gemini.\n"
        "The retrieval precision achieved was 98.7% across 500 test documents."
    )
    page2 = pdf.new_page()
    page2.insert_text(
        (50, 70),
        "AI Research Report 2026 - Page 2\n"
        "Conclusion: In-memory vector caching reduces end-to-end latency to under 250 milliseconds."
    )
    pdf_bytes = pdf.tobytes()
    pdf.close()

    files = {
        "file": ("ai_research_report.pdf", pdf_bytes, "application/pdf")
    }
    upload_res = client.post("/upload", files=files)
    print("Upload status:", upload_res.status_code)
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    print("Upload response:", upload_data)
    doc_id = upload_data["document_id"]
    assert doc_id is not None
    assert upload_data["total_chunks"] > 0

    print("\n--- 4. Testing GET /documents/{doc_id}/pdf ---")
    pdf_res = client.get(f"/documents/{doc_id}/pdf")
    assert pdf_res.status_code == 200, f"Failed to retrieve PDF: {pdf_res.status_code}"
    assert len(pdf_res.content) == len(pdf_bytes), "Retrieved PDF byte count mismatch"
    print(f"PDF download successful ({len(pdf_res.content)} bytes).")

    print("\n--- 5. Testing POST /ask with RAG Question & Citations ---")
    ask_payload = {
        "document_id": doc_id,
        "question": "What retrieval precision was achieved in the research report?"
    }
    ask_res = client.post("/ask", json=ask_payload)
    print("Ask status:", ask_res.status_code)
    assert ask_res.status_code == 200, f"Ask failed: {ask_res.text}"
    ask_data = ask_res.json()
    print("Gemini Answer:\n", ask_data.get("answer"))
    print("\nSources Returned:")
    sources = ask_data.get("sources", [])
    assert len(sources) > 0, "No source chunks returned!"
    for s in sources:
        print(f"  - Page {s.get('page_number')} | Score: {s.get('score'):.4f} | Snippet: {s.get('text')[:80]}...")

    # Validate that answer mentions 98.7% or precision
    answer_text = ask_data.get("answer", "")
    assert "98.7" in answer_text or "precision" in answer_text.lower(), "Expected precision figure in answer!"

    print("\n--- 6. Testing PDF Image Rendering (for Frontend Viewer) ---")
    rendered_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    assert len(rendered_doc) == 2
    pix = rendered_doc.load_page(0).get_pixmap(dpi=140)
    png_bytes = pix.tobytes("png")
    rendered_doc.close()
    assert len(png_bytes) > 1000, "Rendered page image is unexpectedly small"
    print(f"Rendered Page 1 to PNG successfully ({len(png_bytes)} bytes)!")

    print("\n=======================================================")
    print("VERIFICATION COMPLETE: ALL 6 TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")


if __name__ == "__main__":
    test_full_rag_pipeline()
