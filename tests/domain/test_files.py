"""Tests for domain.files utility functions: file name standardization and validation."""

import logging

import pytest

from domain.files import (
    get_year_from_file_name,
    is_valid_account_file,
    standardize_account_file_name,
)


# ------------------------
# Tests for standardize_account_file_name
# ------------------------


@pytest.mark.parametrize(
    'input_name,expected',
    [
        ('kontoauszug_2025_01_januar_extra.pdf', 'kontoauszug_2025_01_januar.pdf'),
        (
            'kontoauszug_2025_01_januar',
            'kontoauszug_2025_01_januar.pdf',
        ),  # missing .pdf
        ('kontoauszug_2025_01', 'kontoauszug_2025_01.pdf'),  # fewer than 4 parts
    ],
)
def test_standardize_account_file_name_valid(input_name, expected):
    """It should correctly standardize a valid account statement file name."""
    assert standardize_account_file_name(input_name) == expected


def test_standardize_account_file_name_error(caplog):
    """It should return None and log an error for invalid input."""
    with caplog.at_level(logging.ERROR):
        result = standardize_account_file_name(None)  # type: ignore
    assert result is None
    assert 'Error standardizing file name' in caplog.text


# ------------------------
# Tests for is_valid_account_file
# ------------------------


@pytest.mark.parametrize(
    'file_name,expected',
    [
        ('kontoauszug_2025_01.pdf', True),
        ('KONTOAUSZUG_2025_01.PDF', True),  # case-insensitive
        ('kontoauszug_2025_01.txt', False),  # wrong extension
        ('otherfile.pdf', False),  # missing keyword
    ],
)
def test_is_valid_account_file(file_name, expected):
    """It should correctly identify valid account statement files."""
    assert is_valid_account_file(file_name) == expected


# ------------------------
# Tests for get_year_from_file_name
# ------------------------


def test_get_year_from_file_name_valid(caplog):
    """It should extract the correct year from a valid file name."""
    with caplog.at_level(logging.INFO):
        result = get_year_from_file_name('kontoauszug_2025_01_januar.pdf')
    assert result == '2025'
    assert 'Extracted year 2025' in caplog.text


def test_get_year_from_file_name_index_error(caplog):
    """It should return None and log an error if the file name has missing parts."""
    with caplog.at_level(logging.ERROR):
        result = get_year_from_file_name('invalidfilename.pdf')
    assert result is None
    assert 'Error extracting year' in caplog.text


def test_get_year_from_file_name_unexpected_error(caplog):
    """It should return None and log an error for unexpected input types."""
    with caplog.at_level(logging.ERROR):
        result = get_year_from_file_name(None)  # type: ignore
    assert result is None
    assert 'Unexpected error' in caplog.text
