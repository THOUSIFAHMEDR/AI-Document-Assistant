import pymupdf as fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF document.

    Args:
        pdf_bytes: PDF file content in bytes.

    Returns:
        List of dictionaries containing page numbers and text.
    """

    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        if not document.is_pdf:
            raise ValueError("Invalid PDF document.")

        extracted_pages = []

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text").strip()

            if text:
                extracted_pages.append({
                    "page_number": page_number,
                    "text": text
                })

        document.close()

        if not extracted_pages:
            raise ValueError(
                "No readable text found. This PDF may be scanned."
            )

        return extracted_pages

    except fitz.FileDataError as error:
        raise ValueError("The PDF file is corrupted or invalid.") from error