import pdfplumber

def extract_text_from_pdf(pdf_file) -> str:
    """Extract all text from an uploaded PDF file object."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")

    if not text.strip():
        raise ValueError("No readable text found in the PDF. Please ensure it is not a scanned image-only PDF.")

    return text.strip()
