"""Tests for process_account_statements orchestration."""

import pandas as pd
import pytest

import processing.statements as states


def fake_append(df, name, value, typ, date):
    """Function to simulate appending of df."""
    new_row = pd.DataFrame([{'Name': name}])
    return pd.concat([df, new_row], ignore_index=True)


@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mock all external dependencies of process_account_statements."""

    # Dummy client and service
    class DummyClient:
        pass

    class DummyService:
        pass

    monkeypatch.setattr(
        states, 'get_google_clients', lambda: (DummyClient(), DummyService())
    )

    # Mock GDrive files
    dummy_files = [
        {'id': 'file1', 'name': 'Kontoauszug_2025_01.pdf'},
        {'id': 'file2', 'name': 'Kontoauszug_2025_02.pdf'},
    ]
    monkeypatch.setattr(
        states, 'get_acc_files_from_gdrive', lambda folder, svc: dummy_files.copy()
    )

    # File validation
    monkeypatch.setattr(states, 'is_valid_account_file', lambda name: True)

    # Standardize file name
    monkeypatch.setattr(states, 'standardize_account_file_name', lambda name: name)

    # File already exists check
    monkeypatch.setattr(states, 'drive_file_exists', lambda name, svc, folder: False)

    # Year extraction
    monkeypatch.setattr(states, 'get_year_from_file_name', lambda name: '2025')

    # PDF text extraction
    monkeypatch.setattr(
        states,
        'extract_text_from_pdf_in_gdrive',
        lambda file_id, svc: 'neuer Kontostand 100\nalter Kontostand 50',
    )

    # Balance extraction
    monkeypatch.setattr(states, 'get_balances_of_account', lambda lines: (1, 2))

    # Transactions
    monkeypatch.setattr(
        states,
        'get_all_transactions',
        lambda lines, old_idx, new_idx: [['01.01.2025 Transaction H 100']],
    )

    # Transaction info extraction
    monkeypatch.setattr(
        states,
        'extract_transaction_info',
        lambda txn, year: ('Transaction', 100.0, 'Einnahme', '2025-01-01'),
    )

    # DataFrame append
    monkeypatch.setattr(states, 'append_transaction', fake_append)

    # Google Sheet open/load/update
    class DummyWorksheet:
        pass

    monkeypatch.setattr(
        states, 'open_worksheet', lambda client, sid, wname: DummyWorksheet()
    )
    monkeypatch.setattr(states, 'load_sheet_to_dataframe', lambda ws: pd.DataFrame())
    monkeypatch.setattr(states, 'update_google_sheet', lambda ws, df: None)

    # Drive move
    monkeypatch.setattr(
        states, 'move_drive_file', lambda file_id, name, old, new, svc: None
    )


def test_process_account_statements_runs(mock_dependencies):
    """It should process account statements without errors."""
    # Just run the function, if no exceptions occur, test passes
    states.process_account_statements()
