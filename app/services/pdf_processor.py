
import re
import pymupdf as fitz


def _normalize(value):
    """Normalize table text for reliable header matching."""
    if not value:
        return ""
    return re.sub(r"\s+", "", str(value)).lower()


def _extract_table_relationships(page):
    """
    Extract student-to-guide relationships from tables.

    Handles vertically merged guide cells by checking whether the
    student's row position falls inside the guide cell's rectangle.
    """
    relationships = []

    try:
        tables = page.find_tables().tables
    except Exception:
        return relationships

    for table in tables:
        rows = table.extract()

        if not rows:
            continue

        # Find the table header.
        header_index = None
        reg_col = name_col = guide_col = None

        for row_index, row in enumerate(rows):
            headers = [_normalize(cell) for cell in row]

            for index, header in enumerate(headers):
                if "universityregno" in header:
                    reg_col = index
                elif "studentname" in header:
                    name_col = index
                elif "internshipguide" in header:
                    guide_col = index

            if reg_col is not None and name_col is not None and guide_col is not None:
                header_index = row_index
                break

            reg_col = name_col = guide_col = None

        if header_index is None:
            continue

        # Collect guide names and their cell coordinates.
        guide_cells = []

        for row_index in range(header_index + 1, len(rows)):
            row = rows[row_index]

            if guide_col >= len(row):
                continue

            guide_text = row[guide_col]
            cell_rect = table.rows[row_index].cells[guide_col]

            if guide_text and cell_rect:
                guide_cells.append({
                    "text": re.sub(r"\s+", " ", guide_text).strip(),
                    "rect": cell_rect
                })

        # Match each student row to the guide cell covering its position.
        for row_index in range(header_index + 1, len(rows)):
            row = rows[row_index]

            if max(reg_col, name_col) >= len(row):
                continue

            reg_no = (row[reg_col] or "").strip()
            student_name = (row[name_col] or "").strip()

            if not reg_no or not student_name:
                continue

            student_rect = table.rows[row_index].cells[name_col]

            if not student_rect:
                continue

            student_center_y = (student_rect[1] + student_rect[3]) / 2

            assigned_guide = None

            for guide in guide_cells:
                y_top = guide["rect"][1]
                y_bottom = guide["rect"][3]

                if y_top <= student_center_y <= y_bottom:
                    assigned_guide = guide["text"]
                    break

            if assigned_guide:
                relationships.append(
                    f"Student: {student_name} | "
                    f"University Registration No: {reg_no} | "
                    f"Internship Guide: {assigned_guide}"
                )

    return relationships


def extract_text_from_pdf(pdf_bytes: bytes) -> list[dict]:
    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    document = None

    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")

        if not document.is_pdf:
            raise ValueError("Invalid PDF document.")

        extracted_pages = []

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            # Extract structured relationships from detected tables.
            relationships = _extract_table_relationships(page)

            if relationships:
                text += "\n\nSTRUCTURED TABLE RECORDS:\n"
                text += "\n".join(relationships)

            if text.strip():
                extracted_pages.append({
                    "page_number": page_number,
                    "text": text
                })

        if not extracted_pages:
            raise ValueError(
                "No readable text found. This PDF may be scanned."
            )

        return extracted_pages

    except fitz.FileDataError as error:
        raise ValueError(
            "The PDF file is corrupted or invalid."
        ) from error

    finally:
        if document is not None:
            document.close()
