"""Tests for Google Sheets update and DataFrame integration functions."""

import pandas as pd

import infrastructure.google_sheets as g_sheets


class DummyWorksheet:
    """Dummy Worksheet for mocking Google Sheets behavior."""

    def __init__(self, values=None):
        """Mock init."""
        self._values = values or []

    def get_all_values(self):
        """Return mocked sheet values."""
        return self._values


class DummySpreadsheet:
    """Dummy Spreadsheet with worksheet retrieval."""

    def __init__(self, worksheets=None):
        """Mock init."""
        self._worksheets = worksheets or {}

    def worksheet(self, name):
        """Return worksheet by name."""
        return self._worksheets[name]


class DummyClient:
    """Dummy client for gspread."""

    def __init__(self, spreadsheet):
        """Mock init."""
        self._spreadsheet = spreadsheet

    def open_by_key(self, key):
        """Return mocked spreadsheet by key."""
        assert key == 'spreadsheet123'
        return self._spreadsheet


# ------------------------
# Tests for open_worksheet
# ------------------------


def test_open_worksheet_opens_correct_sheet():
    """It should open the correct worksheet by spreadsheet ID and name."""
    dummy_ws = DummyWorksheet()
    dummy_spreadsheet = DummySpreadsheet({'MySheet': dummy_ws})
    client = DummyClient(dummy_spreadsheet)

    sheet = g_sheets.open_worksheet(client, 'spreadsheet123', 'MySheet')
    assert sheet is dummy_ws


# ------------------------
# Tests for load_sheet_to_dataframe
# ------------------------


def test_load_sheet_to_dataframe_creates_dataframe():
    """It should load sheet values into a DataFrame with headers applied."""
    values = [['Name', 'Amount'], ['Alice', '10'], ['Bob', '20']]
    ws = DummyWorksheet(values)

    df = g_sheets.load_sheet_to_dataframe(ws)
    assert list(df.columns) == ['Name', 'Amount']
    assert df.iloc[0]['Name'] == 'Alice'
    assert df.iloc[1]['Amount'] == '20'


# ------------------------
# Tests for update_google_sheet
# ------------------------


def test_update_google_sheet_calls_set_with_dataframe(monkeypatch):
    """It should call set_with_dataframe with expected arguments."""
    called_args = {}

    def fake_set_with_dataframe(sheet, df, **kwargs):
        called_args.update(kwargs)
        called_args['df'] = df
        called_args['sheet'] = sheet

    monkeypatch.setattr(g_sheets, 'set_with_dataframe', fake_set_with_dataframe)

    ws = DummyWorksheet()
    df = pd.DataFrame({'Name': ['Alice'], 'Amount': [10]})

    g_sheets.update_google_sheet(ws, df)

    assert called_args['sheet'] is ws
    assert called_args['df'].equals(df)
    assert called_args['row'] == 2
    assert called_args['col'] == 1
    assert called_args['include_index'] is False
    assert called_args['include_column_header'] is False
    assert called_args['resize'] is False
