"""This module contains tests for transaction-related functions."""

from datetime import date
import logging

import pandas as pd
import pytest

from domain.transactions import (
    append_transaction,
    check_income_or_expense,
    extract_transaction_info,
    get_all_transactions,
    get_transaction_value,
)


# ------------------------
# Tests for get_all_transactions
# ------------------------


def test_get_all_transactions_valid(caplog):
    """Test extracting transactions from sample lines."""
    lines = [
        'alter Kontostand 1.000,00 EUR',
        '01.01. 02.01. Zahlung Supermarkt 50,00 S',
        'weitere Details',
        '03.01. 04.01. Gehalt 2.000,00 H',
        'neuer Kontostand 2.950,00 EUR',
    ]
    with caplog.at_level(logging.INFO):
        txns = get_all_transactions(lines, 0, len(lines) - 1)

    assert len(txns) == 2
    assert txns[0][0].startswith('01.01.')
    assert 'Extracted 2 transactions' in caplog.text


def test_get_all_transactions_invalid_indices(caplog):
    """Test handling of invalid balance indices."""
    lines = ['foo', 'bar']
    with caplog.at_level(logging.ERROR):
        txns = get_all_transactions(lines, -1, 1)
    assert txns == []
    assert 'Invalid balance indices' in caplog.text


def test_get_all_transactions_handles_error(caplog):
    """Test handling of unexpected errors."""
    with caplog.at_level(logging.ERROR):
        txns = get_all_transactions(None, 0, 1)  # type: ignore
    assert txns == []
    assert 'Error extracting transactions' in caplog.text


# ------------------------
# Tests for get_transaction_value
# ------------------------


def test_get_transaction_value_valid():
    """Test extracting transaction value from valid transaction."""
    txn = ['01.01. 02.01. Einkauf 100,00 S']
    value = get_transaction_value(txn)
    assert value == pytest.approx(100.0)


def test_get_transaction_value_invalid_format(caplog):
    """Test handling of invalid transaction format."""
    txn = ['01.01. 02.01. Einkauf ABC']
    with caplog.at_level(logging.ERROR):
        value = get_transaction_value(txn)
    assert value == 0.0
    assert 'Error extracting transaction value' in caplog.text


def test_get_transaction_value_empty(caplog):
    """Test handling of empty transaction list."""
    with caplog.at_level(logging.ERROR):
        value = get_transaction_value([])
    assert value == 0.0
    assert 'Empty transaction' in caplog.text


# ------------------------
# Tests for check_income_or_expense
# ------------------------


@pytest.mark.parametrize(
    'txn,expected',
    [
        (['01.01. Einkauf 10,00 S'], 'Ausgabe'),
        (['01.01. Gehalt 2000,00 H'], 'Einnahme'),
        (['01.01. Sonstiges'], 'Unbekannt'),
        ([], 'Unbekannt'),
    ],
)
def test_check_income_or_expense(txn, expected):
    """Test determining transaction type."""
    assert check_income_or_expense(txn) == expected


# ------------------------
# Tests for extract_transaction_info
# ------------------------


def test_extract_transaction_info_valid():
    """Test extracting all transaction info from valid transaction."""
    txn = ['01.01. 02.01. Einkauf 100,00 S', 'Supermarkt']
    name, value, ttype, tdate = extract_transaction_info(txn, '2025')
    assert name == 'Supermarkt'
    assert value == pytest.approx(100.0)
    assert ttype == 'Ausgabe'
    assert tdate == date(2025, 1, 1)


def test_extract_transaction_info_default_name():
    """Test default name for transactions without a second line."""
    txn = ['01.01. 02.01. Bareinzahlung 50,00 H']
    name, value, ttype, tdate = extract_transaction_info(txn, '2025')
    assert name == 'Bareinzahlung'
    assert value == pytest.approx(50.0)
    assert ttype == 'Einnahme'
    assert tdate == date(2025, 1, 1)


# ------------------------
# Tests for append_transaction
# ------------------------


def test_append_transaction_adds_row():
    """Test appending a transaction to the DataFrame."""
    df = pd.DataFrame(columns=['Name', 'Wert', 'Typ', 'Datum', 'Col5', 'Col6'])
    append_transaction(df, 'Supermarkt', 100.0, 'Ausgabe', date(2025, 1, 1))
    assert len(df) == 1
    row = df.iloc[0]
    assert row['Name'] == 'Supermarkt'
    assert row['Wert'] == 100.0
    assert row['Typ'] == 'Ausgabe'
    assert row['Datum'] == date(2025, 1, 1)
