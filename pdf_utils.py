"""
pdf_utils.py
------------
Handles reading uploaded PDF files and extracting their text content using PyMuPDF (fitz).
Designed to detect and report empty or scanned (image-only) PDFs gracefully.
"""

from typing import BinaryIO
import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    """Custom exception raised when text extraction fails or PDF is invalid."""
    pass


# Function to extract all readable text from an uploaded PDF file
# Why: Streamlit passes an in-memory byte buffer (UploadedFile). We read its bytes into PyMuPDF,
# loop through each page, extract text, and verify that there is actual readable text.
def extract_text(pdf_file: BinaryIO) -> str:
    """
    Extracts plain text from a PDF file stream.

    Args:
        pdf_file: A binary file-like object (e.g. Streamlit's UploadedFile).

    Returns:
        str: The combined text extracted from all pages.

    Raises:
        PDFExtractionError: If the PDF is empty, corrupted, or scanned (image-only).
    """
    try:
        # Read the raw bytes from the uploaded file
        pdf_bytes = pdf_file.read()
        
        # Rewind pointer so the file can be re-read if needed
        pdf_file.seek(0)

        if not pdf_bytes:
            raise PDFExtractionError("Uploaded file is empty (0 bytes). Please upload a valid PDF.")

        # Open the PDF directly from memory stream
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    except Exception as e:
        if isinstance(e, PDFExtractionError):
            raise e
        raise PDFExtractionError(f"Could not open PDF file. Details: {str(e)}")

    if len(doc) == 0:
        doc.close()
        raise PDFExtractionError("This PDF has 0 pages. Please upload a valid document.")

    extracted_pages: list[str] = []

    # Iterate through each page and extract text
    for page_number in range(len(doc)):
        page = doc[page_number]
        page_text = page.get_text()
        if page_text:
            extracted_pages.append(page_text.strip())

    doc.close()

    full_text = "\n\n".join(extracted_pages).strip()

    # Check if the extracted text is empty or just whitespace (common in scanned documents)
    if not full_text:
        raise PDFExtractionError(
            "Is PDF me koi readable text nahi mila! Ye ek scanned ya image-only PDF lagti hai. "
            "Kripya digital notes ya typed textbook chapter upload karein."
        )

    return full_text

