"""Tests for Google authentication helper functions."""

import logging

import pytest

import infrastructure.google_auth as google_auth


class DummyCreds:
    """Dummy credentials object for mocking."""

    pass


class DummyClient:
    """Dummy gspread client for mocking."""

    pass


class DummyService:
    """Dummy Google Drive service for mocking."""

    pass


@pytest.fixture
def mock_local_auth(monkeypatch):
    """Fixture to mock local ServiceAccount JSON authentication."""
    monkeypatch.setattr(google_auth.os.path, 'exists', lambda path: True)

    def fake_from_json_keyfile_name(path, scopes):
        assert 'dummy.json' in path
        assert scopes == google_auth.SCOPES
        return DummyCreds()

    monkeypatch.setattr(
        google_auth.ServiceAccountCredentials,
        'from_json_keyfile_name',
        fake_from_json_keyfile_name,
    )
    monkeypatch.setattr(google_auth.gspread, 'authorize', lambda creds: DummyClient())
    monkeypatch.setattr(
        google_auth, 'build', lambda name, ver, credentials=None: DummyService()
    )


@pytest.fixture
def mock_default_auth(monkeypatch):
    """Fixture to mock Cloud Run default authentication."""
    monkeypatch.setattr(google_auth.os.path, 'exists', lambda path: False)

    def fake_default(scopes=None):
        assert scopes == google_auth.SCOPES
        return DummyCreds(), 'project'

    monkeypatch.setattr(google_auth.google.auth, 'default', fake_default)
    monkeypatch.setattr(google_auth.gspread, 'authorize', lambda creds: DummyClient())
    monkeypatch.setattr(
        google_auth, 'build', lambda name, ver, credentials=None: DummyService()
    )


def test_get_google_clients_local_json(mock_local_auth, capsys, caplog):
    """It should return client and service when using local JSON credentials."""
    with caplog.at_level(logging.INFO):
        client, service = google_auth.get_google_clients('dummy.json')
    assert isinstance(client, DummyClient)
    assert isinstance(service, DummyService)
    assert 'Using local JSON credentials' in caplog.text


def test_get_google_clients_default_credentials(mock_default_auth, capsys, caplog):
    """It should return client and service when using default Cloud Run credentials."""
    with caplog.at_level(logging.INFO):
        client, service = google_auth.get_google_clients('nonexistent.json')
    assert isinstance(client, DummyClient)
    assert isinstance(service, DummyService)
    assert 'Using default Cloud Run credentials' in caplog.text
