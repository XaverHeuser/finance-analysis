"""Tests for PDF text extraction functions."""

import logging

import infrastructure.pdf_parser as pdf_parser


# ------------------------
# Mocks for pdfplumber
# ------------------------


class DummyPage:
    """Mock page object with extract_text."""

    def __init__(self, text):
        """Mock init."""
        self._text = text

    def extract_text(self, extraction_mode=None):
        """Mock text extracting."""
        return self._text


class DummyPDF:
    """Mock pdf object with pages."""

    def __init__(self, pages):
        """Mock init."""
        self.pages = pages

    def __enter__(self):
        """Mock enter."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Mock exit."""
        return False


# ------------------------
# Tests for extract_text_from_pdf_in_gdrive
# ------------------------


def test_extract_text_from_pdf_in_gdrive(monkeypatch):
    """It should extract text from PDF bytes returned by service."""
    file_content = b'%PDF-1.4 content'

    # Mock the service
    class DummyRequest:
        def execute(self):
            return file_content

    class DummyService:
        def files(self):
            return self

        def get_media(self, fileId):  # noqa: N803
            return DummyRequest()

    # Mock pdfplumber.open to return DummyPDF
    monkeypatch.setattr(
        pdf_parser.pdfplumber,
        'open',
        lambda f: DummyPDF([DummyPage('Page1'), DummyPage('Page2')]),
    )

    text = pdf_parser.extract_text_from_pdf_in_gdrive('file123', DummyService())
    assert 'Page1' in text
    assert 'Page2' in text


def test_extract_text_from_pdf_in_gdrive_handles_page_error(monkeypatch, caplog):
    """It should log a warning if a page fails extraction."""

    class BadPage:
        def extract_text(self, extraction_mode=None):
            raise ValueError('bad page')

    class DummyRequest:
        def execute(self):
            return b'%PDF dummy content'

    class DummyService:
        def files(self):
            return self

        def get_media(self, fileId):  # noqa: N803
            return DummyRequest()

    # Then patch pdfplumber.open as before
    monkeypatch.setattr(pdf_parser.pdfplumber, 'open', lambda f: DummyPDF([BadPage()]))

    with caplog.at_level(logging.WARNING):
        text = pdf_parser.extract_text_from_pdf_in_gdrive('file123', DummyService())

    assert text == ''
    assert 'Failed to extract text from a page' in caplog.text


def test_extract_text_from_pdf_in_gdrive_handles_api_error(caplog):
    """It should log an error if service call fails."""

    class BadService:
        def files(self):
            return self

        def get_media(self, fileid):
            raise RuntimeError('API error')

    with caplog.at_level(logging.ERROR):
        text = pdf_parser.extract_text_from_pdf_in_gdrive('file123', BadService())
    assert text == ''
    assert 'An error occurred while extracting text' in caplog.text


# ------------------------
# Tests for extract_pdf_lines
# ------------------------


def test_extract_pdf_lines_normal(caplog):
    """It should split text into lines."""
    text = 'Line1\nLine2\nLine3'
    with caplog.at_level(logging.DEBUG):
        lines = pdf_parser.extract_pdf_lines(text)
    assert lines == ['Line1', 'Line2', 'Line3']
    assert 'Extracted 3 lines' in caplog.text


def test_extract_pdf_lines_empty(caplog):
    """It should handle empty text."""
    with caplog.at_level(logging.DEBUG):
        lines = pdf_parser.extract_pdf_lines('')
    assert lines == ['']
    assert 'Extracted 1 lines' in caplog.text


def test_extract_pdf_lines_handles_exception(caplog):
    """It should log an error if input is not a string."""
    with caplog.at_level(logging.ERROR):
        lines = pdf_parser.extract_pdf_lines(None)  # type: ignore
    assert lines == []
    assert 'Error splitting PDF text' in caplog.text


# ------------------------
# Tests for extract_text_from_pdf_in_local
# ------------------------


def test_extract_text_from_pdf_in_local(tmp_path, monkeypatch):
    """It should extract text from a local PDF file."""
    pdf_file = tmp_path / 'test.pdf'
    pdf_file.write_bytes(b'%PDF content')

    monkeypatch.setattr(
        pdf_parser.pdfplumber, 'open', lambda f: DummyPDF([DummyPage('PageX')])
    )
    text = pdf_parser.extract_text_from_pdf_in_local(pdf_file)
    assert 'PageX' in text


def test_extract_text_from_pdf_in_local_file_not_found(tmp_path, caplog):
    """It should log an error if the file does not exist."""
    missing_file = tmp_path / 'missing.pdf'
    with caplog.at_level(logging.ERROR):
        text = pdf_parser.extract_text_from_pdf_in_local(missing_file)
    assert text == ''
    assert 'File could not be found' in caplog.text


def test_extract_text_from_pdf_in_local_handles_exception(
    tmp_path, monkeypatch, caplog
):
    """It should log an error if pdfplumber.open raises an exception."""
    pdf_file = tmp_path / 'test.pdf'
    pdf_file.write_bytes(b'%PDF content')

    class BadPDF:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            """Mock exit."""
            return False

        @property
        def pages(self):
            raise RuntimeError('bad read')

    monkeypatch.setattr(pdf_parser.pdfplumber, 'open', lambda f: BadPDF())

    with caplog.at_level(logging.ERROR):
        text = pdf_parser.extract_text_from_pdf_in_local(pdf_file)
    assert text == ''
    assert 'An unexpected error occurred while reading' in caplog.text
