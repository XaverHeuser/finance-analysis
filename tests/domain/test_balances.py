"""Tests for domain.balances functions: balance extraction and account totals."""

import logging

import pytest

from domain.balances import (
    extract_balance_from_line,
    get_balance_of_account,
    get_balances_of_account,
)


# ------------------------
# Tests for extract_balance_from_line
# ------------------------


def test_extract_balance_from_valid_line():
    """It should correctly extract a float balance from a valid line."""
    line = 'Datum 01.01.2025 neuer Kontostand 1.234,56 EUR'
    result = extract_balance_from_line(line)
    assert result == pytest.approx(1234.56)


def test_extract_balance_with_invalid_number(caplog):
    """It should return 0.0 and log an error if the number is invalid."""
    line = 'neuer Kontostand ABC EUR'
    with caplog.at_level(logging.ERROR):
        result = extract_balance_from_line(line)
    assert result == 0.0
    assert 'Fehler' in caplog.text


def test_extract_balance_with_empty_line(caplog):
    """It should return 0.0 and log an error for an empty line."""
    line = ''
    with caplog.at_level(logging.ERROR):
        result = extract_balance_from_line(line)
    assert result == 0.0
    assert 'error' in caplog.text.lower()


# ------------------------
# Tests for get_balance_of_account
# ------------------------


def test_get_balance_of_account_old_balance():
    """It should return the first matching 'alter Kontostand' line."""
    lines = [
        '01.01.2025 alter Kontostand 1.000,00 EUR',
        '01.01.2025 neuer Kontostand 2.000,00 EUR',
    ]
    result = get_balance_of_account(lines, 'alter Kontostand')
    assert result == (1000.00, 0)


def test_get_balance_of_account_new_balance():
    """It should return the last matching 'neuer Kontostand' line."""
    lines = [
        '01.01.2025 alter Kontostand 1.000,00 EUR',
        '01.01.2025 neuer Kontostand 2.000,00 EUR',
    ]
    result = get_balance_of_account(lines, 'neuer Kontostand')
    assert result == (2000.00, 1)


def test_get_balance_of_account_not_found(caplog):
    """It should return (0.0, -1) and log an error if the balance type is missing."""
    lines = ['Some unrelated line']
    with caplog.at_level(logging.ERROR):
        result = get_balance_of_account(lines, 'neuer Kontostand')
    assert result == (0.0, -1)
    assert 'not found' in caplog.text


# ------------------------
# Tests for get_balances_of_account
# ------------------------


def test_get_balances_of_account_happy_path(caplog):
    """It should return indices of old and new balances and log info messages."""
    lines = [
        '01.01.2025 alter Kontostand 1.000,00 EUR',
        '01.01.2025 neuer Kontostand 2.000,00 EUR',
    ]
    with caplog.at_level(logging.INFO):
        result = get_balances_of_account(lines)
    assert result == (0, 1)
    assert 'Old balance' in caplog.text
    assert 'New balance' in caplog.text


def test_get_balances_of_account_with_missing_lines():
    """It should return (-1, -1) if no balances are found."""
    lines = ['just a random line']
    result = get_balances_of_account(lines)
    assert result == (-1, -1)
