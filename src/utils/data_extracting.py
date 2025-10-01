"""This module includes function for data extracting from Folder and pdf-Docs."""

from io import BytesIO
import logging
import re
from typing import Any

import pdfplumber

from src.models.models import DriveFile


def get_acc_files_from_gdrive_folder(folder_id: str, service: Any) -> list[DriveFile]:
    """List all files in a specified Google Drive folder."""
    try:
        # Build query to fetch all files inside the folder (not trashed)
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields='files(id, name)').execute()
        items: list[DriveFile] = results.get('files', [])

        if not items:
            logging.warning('No files found.')
            return []

        # Sort files alphabetically by name
        items = sorted(items, key=lambda x: x['name'])

        # Print files for debugging/informational purposes
        logging.info(f'Found {len(items)} files in folder {folder_id}')
        for item in items:
            logging.debug(f'File: {item["name"]} (ID: {item["id"]})')

        return items

    except Exception as e:
        logging.error(
            f'An error occurred while fetching files from folder {folder_id}: {e}'
        )
        return []


def extract_text_from_pdf(file_id: str, service: Any) -> str:
    """Extract the text from a pdf file in GDrive."""
    try:
        # Request file content from Google Drive API
        request = service.files().get_media(fileId=file_id)
        file_data = request.execute()

        # Open PDF from bytes and extract text page by page
        with pdfplumber.open(BytesIO(file_data)) as pdf:
            full_pdf_text = ''
            for page in pdf.pages:
                try:
                    # Use layout mode to preserve formatting as much as possible
                    text = page.extract_text(extraction_mode='layout') or ''
                    full_pdf_text += text
                except Exception as page_err:
                    logging.warning(
                        f'Failed to extract text from a page in {file_id}: {page_err}'
                    )
            return full_pdf_text

    except Exception as e:
        logging.error(
            f'An error occurred while extracting text from PDF with ID {file_id}: {e}'
        )
        return ''


def extract_balance_from_line(line: str) -> float:
    """Extract the balance from a line of text."""
    try:
        # Get the balance and convert to float
        balance_str = line.split()[-2]
        balance_str = balance_str.replace('.', '').replace(',', '.')
        return float(balance_str)

    except (IndexError, ValueError) as e:
        logging.error(
            f'An error occurred when trying to extract the balance of a line: {line}. Fehler: {e}'
        )
        return 0.0

    except Exception as e:
        logging.error(f'Unexpected error in extract_balance_from_line: {e}')
        return 0.0


def get_balance_of_account(lines: list[str], balance_type: str) -> tuple[float, int]:
    """Get all balances (old or new) of an account."""
    try:
        results = []
        for idx, line in enumerate(lines):
            if balance_type in line:
                # Extract numeric balance from line
                balance_float = extract_balance_from_line(line)
                results.append((balance_float, idx))

        if not results:
            logging.error(f'{balance_type} not found.')
            return (0.0, -1)

        if balance_type == 'neuer Kontostand':
            return results[-1]
        if balance_type == 'alter Kontostand':
            return results[0]
        else:
            return results[0]

    except Exception as e:
        logging.error(f'Error getting balance of account ({balance_type}): {e}')
        return (0.0, -1)


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

        return transactions

    except Exception as e:
        logging.error(f'Error extracting transactions: {e}')
        return []


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
