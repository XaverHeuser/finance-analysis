"""This module includes function for data extracting from Folder and pdf-Docs."""

import logging
from pathlib import Path
import re

import pdfplumber


def get_all_account_statement_files(downloads_path: Path) -> list[Path]:
    """Get all the account statement files from the downloads folder."""
    return [
        file
        for file in downloads_path.iterdir()
        if 'Kontoauszug' in file.name and file.is_file()
    ]


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract the text from a pdf file."""
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


def extract_balance_from_line(line: str) -> float:
    """Extract the balance from a line of text."""
    try:
        parts = line.split(' ')
        balance_str = parts[-2]
        balance_str = balance_str.replace('.', '').replace(',', '.')
        return float(balance_str)
    except (IndexError, ValueError) as e:
        logging.error(
            f'An error occurred when trying to extract the balance of a line: {line}. Fehler: {e}'
        )
        return 0.0


def get_balance_of_account(lines: list, balance_type: str) -> list:
    """Get all balances (old or new) of an account."""
    results = []
    for idx, line in enumerate(lines):
        if balance_type in line:
            balance_float = extract_balance_from_line(line)
            results.append((balance_float, idx))
    if not results:
        logging.error(f'{balance_type} not found.')
    else:
        if balance_type == 'neuer Kontostand':
            results = results[-1]
        if balance_type == 'alter Kontostand':
            results = results[0]
    return results


def get_all_transactions(
    lines: list, old_balance_idx: int, new_balance_idx: int
) -> list:
    """Extract all transactions from an account statement between two index markers."""
    transactions_part = lines[old_balance_idx + 1 : new_balance_idx]
    pattern_transaction_start = re.compile(r'\d{2}\.\d{2}\. \d{2}\.\d{2}\.')
    pattern_transaction_start_alt = re.compile(r'Übertrag')

    transactions = []
    current_transaction = []

    for line in transactions_part:
        # If line starts with Übertrag or with pattern_transaction_start, then it is a new transaction
        if pattern_transaction_start_alt.match(line) or pattern_transaction_start.match(
            line
        ):
            transactions.append(current_transaction)
            current_transaction = []
        current_transaction.append(line)

    transactions.append(current_transaction)  # Append the last transaction

    print(transactions)
    transactions = transactions[1:]  # Remove the empty first transaction

    # Filter out transactions that start with 'Übertrag'
    transactions = [
        txn for txn in transactions if not pattern_transaction_start_alt.match(txn[0])
    ]

    for txn in transactions:
        # Append all lines after line 2 (name) and keep only the first two lines
        if len(txn) > 2:
            txn[2] = ''.join(txn[1:])
            del txn[3:]

    return transactions


def check_income_or_expense(transaction: list[str]) -> str:
    """Check if the transaction is an income or an expense based on its first line."""
    if not transaction:
        return 'Unknown'

    line = transaction[0]
    if re.match(r'.*S$', line):
        return 'Expense'
    elif re.match(r'.*H$', line):
        return 'Income'
    return 'Unknown'


def get_transaction_value(transaction: list) -> float:
    """Get the value of the transaction."""
    value = transaction[0].split(' ')[-2]
    value_float = float(value.replace('.', '').replace(',', '.'))

    return value_float
