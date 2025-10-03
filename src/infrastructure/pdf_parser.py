"""Module for extracting text from PDF files stored in Google Drive."""

from io import BytesIO
import logging
from pathlib import Path
from typing import Any

import pdfplumber


def extract_text_from_pdf_in_gdrive(file_id: str, service: Any) -> str:
    """Extract the text from a pdf file in GDrive."""
    try:
        # Request file content from Google Drive API
        request = service.files().get_media(fileId=file_id)
        file_data = request.execute()

        # Open PDF from bytes and extract text page by page
        with pdfplumber.open(BytesIO(file_data)) as pdf:
            full_pdf_text = ''
            for page in pdf.pages:
                try:
                    # Use layout mode to preserve formatting as much as possible
                    text = page.extract_text(extraction_mode='layout') or ''
                    full_pdf_text += text
                except Exception as page_err:
                    logging.warning(
                        f'Failed to extract text from a page in {file_id}: {page_err}'
                    )
            return full_pdf_text

    except Exception as e:
        logging.error(
            f'An error occurred while extracting text from PDF with ID {file_id}: {e}'
        )
        return ''


def extract_pdf_lines(full_pdf_text: str) -> list[str]:
    """Split the full PDF text into individual lines."""
    try:
        lines = full_pdf_text.split('\n')
        logging.debug(f'Extracted {len(lines)} lines from PDF.')
        return lines
    except Exception as e:
        logging.error(f'Error splitting PDF text into lines: {e}')
        return []


def extract_text_from_pdf_in_local(pdf_path: Path) -> str:
    """Extract the text from a pdf file in local storage."""
    if not pdf_path.exists():
        logging.error(f'File could not be found: {pdf_path}')
        return ''

    full_pdf_text = ''

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                full_pdf_text += page.extract_text(extraction_mode='layout')
    except Exception as e:
        logging.error(f'An unexpected error occurred while reading {pdf_path}: {e}')

    return full_pdf_text
