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


def test_merged_guide_cell_mapping():
    """Verify that students inside a merged guide cell get the correct guide."""

    doc = fitz.open()
    page = doc.new_page()

    # Table coordinates
    x = [50, 140, 250, 380, 520]
    y = [80, 110, 140, 170, 200]

    # Draw vertical borders
    for xpos in x:
        page.draw_line((xpos, y[0]), (xpos, y[-1]), width=1)

    # Draw outer and header horizontal borders
    for ypos in [y[0], y[1], y[-1]]:
        page.draw_line((x[0], ypos), (x[-1], ypos), width=1)

    # Draw student-row separators only up to the guide column.
    # This creates one vertically merged guide cell.
    for ypos in [y[2], y[3]]:
        page.draw_line((x[0], ypos), (x[3], ypos), width=1)

    # Table headers
    headers = [
        "Sl No",
        "University Reg No",
        "Student Name",
        "Internship Guide"
    ]

    for i, header in enumerate(headers):
        page.insert_text((x[i] + 5, 100), header, fontsize=8)

    # Three students
    students = [
        ("1", "U19MT24S0023", "Student One"),
        ("2", "U19MT24S0024", "Thousif Ahmed R"),
        ("3", "U19MT24S0025", "Student Three"),
    ]

    for row_index, student in enumerate(students):
        baseline = 130 + row_index * 30

        for col_index, value in enumerate(student):
            page.insert_text(
                (x[col_index] + 5, baseline),
                value,
                fontsize=8
            )

    # One guide name in the merged cell
    page.insert_text((x[3] + 5, 130), "Mrs Shanthy M", fontsize=8)
    page.insert_text(
        (x[3] + 5, 145),
        "(Assistant Professor)",
        fontsize=8
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    result = extract_text_from_pdf(pdf_bytes)

    extracted_text = "\n".join(
        item["text"] for item in result
    )


    assert (
        "Student: ThousifAhmedR | "
        "University Registration No: U19MT24S0024 | "
        "Internship Guide: MrsShanthyM (AssistantProfessor)"
    ) in extracted_text
