import pymupdf as fitz
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.pdf_processor import extract_text_from_pdf


def test_pdf_extraction():

    # Create a sample PDF in memory
    doc = fitz.open()

    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "AI Document Assistant - PDF Extraction Test"
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    # Extract text
    result = extract_text_from_pdf(pdf_bytes)

    assert len(result) == 1
    assert result[0]["page_number"] == 1
    assert "AI Document Assistant" in result[0]["text"]

    print("SUCCESS: PDF text extraction is working!")
    print("Extracted text:", result[0]["text"])


if __name__ == "__main__":
    test_pdf_extraction()