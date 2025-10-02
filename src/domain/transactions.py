"""Module for handling transactions."""

from datetime import date
import logging
import re

import pandas as pd


def get_all_transactions(
    lines: list[str], old_balance_idx: int, new_balance_idx: int
) -> list[list[str]]:
    """Extract all transactions from an account statement between two index markers."""
    try:
        # Ensure indices are valid
        if (
            old_balance_idx < 0
            or new_balance_idx <= old_balance_idx
            or new_balance_idx > len(lines)
        ):
            logging.error(
                f'Invalid balance indices: old={old_balance_idx}, new={new_balance_idx}'
            )
            return []

        # Get only the lines between old and new balance
        transactions_part = lines[old_balance_idx + 1 : new_balance_idx]
        pattern_start = re.compile(r'\d{2}\.\d{2}\. \d{2}\.\d{2}\.')
        pattern_alt = re.compile(r'Übertrag')

        transactions: list[list[str]] = []
        current_transaction: list[str] = []

        for line in transactions_part:
            # If line starts with Übertrag or with pattern_transaction_start, then it is a new transaction
            if pattern_alt.match(line) or pattern_start.match(line):
                transactions.append(current_transaction)
                current_transaction = []
            current_transaction.append(line)

        transactions.append(current_transaction)  # Append the last transaction
        transactions = transactions[1:]  # Remove the empty first transaction
        # Filter out transactions that start with 'Übertrag'
        transactions = [txn for txn in transactions if not pattern_alt.match(txn[0])]

        for txn in transactions:
            # Append all lines after line 2 (name) and keep only the first two lines
            if len(txn) > 2:
                txn[2] = ''.join(txn[1:])
                del txn[3:]

        logging.info(f'Extracted {len(transactions)} transactions.')
        return transactions

    except Exception as e:
        logging.error(f'Error extracting transactions: {e}')
        return []


def extract_transaction_info(
    transaction: list[str], transaction_year: str
) -> tuple[str, float, str, date]:
    """Return transaction type, DataFrame, name, value, and month."""
    logging.info(f'Checking transaction {transaction}...')

    transaction_name = (
        transaction[1].strip() if len(transaction) > 1 else 'Bareinzahlung'
    )
    transaction_value = get_transaction_value(transaction)
    transaction_type = check_income_or_expense(transaction)

    date_str = str(transaction[0].split(' ')[0] + transaction_year)
    transaction_date = pd.to_datetime(date_str, format='%d.%m.%Y').date()

    return transaction_name, transaction_value, transaction_type, transaction_date


def get_transaction_value(transaction: list[str]) -> float:
    """Get the value of the transaction."""
    try:
        if not transaction:
            logging.error('Empty transaction passed to get_transaction_value')
            return 0.0

        # Extract the value from the transaction line
        value = transaction[0].split()[-2]
        return float(value.replace('.', '').replace(',', '.'))

    except (IndexError, ValueError) as e:
        logging.error(f'Error extracting transaction value: {transaction}. Fehler: {e}')
        return 0.0
    except Exception as e:
        logging.error(f'Unexpected error in get_transaction_value: {e}')
        return 0.0


def check_income_or_expense(transaction: list[str]) -> str:
    """Check if the transaction is an income or an expense based on its first line."""
    try:
        if not transaction:
            return 'Unbekannt'

        line = transaction[0]

        # Transactions ending with 'S' → expense, 'H' → income
        if line.endswith('S'):
            return 'Ausgabe'
        elif line.endswith('H'):
            return 'Einnahme'
        return 'Unbekannt'

    except Exception as e:
        logging.error(f'Error determining income/expense: {e}')
        return 'Unbekannt'


def append_transaction(
    df: pd.DataFrame, t_name: str, t_value: float, t_type: str, t_date: date
) -> None:
    """Append a new row to the DataFrame."""
    # Append new row to DataFrame
    df.loc[len(df)] = [t_name, t_value, t_type, t_date, None, None]
