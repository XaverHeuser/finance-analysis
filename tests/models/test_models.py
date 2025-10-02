"""Unit tests for the DriveFile model in models.py."""

from models.models import DriveFile


def test_drive_file_initialization():
    """Test that a DriveFile instance is initialized correctly."""
    file = DriveFile(id='12345', name='test_document.pdf')
    assert file.id == '12345'
    assert file.name == 'test_document.pdf'


def test_drive_file_equality():
    """Test the equality comparison of DriveFile instances."""
    file1 = DriveFile(id='12345', name='test_document.pdf')
    file2 = DriveFile(id='12345', name='test_document.pdf')
    file3 = DriveFile(id='67890', name='other.pdf')

    assert file1 == file2
    assert file1 != file3


def test_drive_file_repr():
    """Test the string representation of a DriveFile instance."""
    file = DriveFile(id='12345', name='test_document.pdf')
    repr_str = repr(file)
    assert 'DriveFile' in repr_str
    assert '12345' in repr_str
    assert 'test_document.pdf' in repr_str
