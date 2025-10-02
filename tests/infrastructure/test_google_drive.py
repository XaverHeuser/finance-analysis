"""Tests for Google Drive file operations."""

import logging

import infrastructure.google_drive as g_drive


class DummyFiles:
    """Dummy files resource for mocking Drive service."""

    def __init__(self, results=None, fail=False):
        """Mock init."""
        self._results = results or {}
        self._fail = fail

    def list(self, q=None, fields=None):
        """Mock file listing."""
        if self._fail:
            raise RuntimeError('API error')
        return DummyExecute(self._results)

    def update(self, **kwargs):
        """Mock update."""
        return DummyExecute({'updated': kwargs})


class DummyExecute:
    """Dummy object that simulates execute()."""

    def __init__(self, result):
        """Mock init."""
        self._result = result

    def execute(self):
        """Mock execution."""
        return self._result


class DummyService:
    """Dummy Drive service with .files()."""

    def __init__(self, results=None, fail=False):
        """Mock init."""
        self._files = DummyFiles(results, fail)

    def files(self):
        """Mock file returning."""
        return self._files


# ------------------------
# Tests for drive_file_exists
# ------------------------


def test_drive_file_exists_true():
    """Test that drive_file_exists returns True when file exists."""
    service = DummyService({'files': [{'id': '1', 'name': 'test.pdf'}]})
    exists = g_drive.drive_file_exists('test.pdf', service, 'folder123')
    assert exists is True


def test_drive_file_exists_false():
    """Test that drive_file_exists returns False when file does not exist."""
    service = DummyService({'files': []})
    exists = g_drive.drive_file_exists('missing.pdf', service, 'folder123')
    assert exists is False


# ------------------------
# Tests for move_drive_file
# ------------------------


def test_move_drive_file_logs(caplog):
    """Test that move_drive_file logs the correct info message."""
    service = DummyService()
    with caplog.at_level(logging.INFO):
        g_drive.move_drive_file('file123', 'new.pdf', 'oldfolder', 'newfolder', service)
    assert 'file123' in caplog.text
    assert 'newfolder' in caplog.text


# ------------------------
# Tests for get_acc_files_from_gdrive
# ------------------------


def test_get_acc_files_from_gdrive_sorted(caplog):
    """Test that get_acc_files_from_gdrive returns files sorted by name."""
    unsorted = {
        'files': [{'id': '2', 'name': 'zeta.pdf'}, {'id': '1', 'name': 'alpha.pdf'}]
    }
    service = DummyService(unsorted)
    with caplog.at_level(logging.INFO):
        files = g_drive.get_acc_files_from_gdrive('folder123', service)
    assert [f['name'] for f in files] == ['alpha.pdf', 'zeta.pdf']
    assert 'Found 2 files' in caplog.text


def test_get_acc_files_from_gdrive_no_files(caplog):
    """Test that get_acc_files_from_gdrive handles no files found."""
    service = DummyService({'files': []})
    with caplog.at_level(logging.WARNING):
        files = g_drive.get_acc_files_from_gdrive('folder123', service)
    assert files == []
    assert 'No files found' in caplog.text


def test_get_acc_files_from_gdrive_exception(caplog):
    """Test that get_acc_files_from_gdrive handles exceptions."""
    service = DummyService(fail=True)
    with caplog.at_level(logging.ERROR):
        files = g_drive.get_acc_files_from_gdrive('folder123', service)
    assert files == []
    assert 'An error occurred' in caplog.text
