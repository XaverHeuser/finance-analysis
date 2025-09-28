"""This module includes function for data extracting from Folder and pdf-Docs."""

from io import BytesIO
import logging
from pathlib import Path
import re
from typing import Any, TypedDict

import pdfplumber


# TODO: Clean functions
# TODO: Add comments
# TODO: Add type hints
# TODO: Add error handling
# TODO: Explain classes / Enhance classes / outsource to separate file?


class DriveFile(TypedDict):
    """TypedDict for a file in Google Drive."""

    id: str
    name: str


def get_all_account_statement_files(downloads_path: Path) -> list[Path]:
    """Get all the account statement files from the downloads folder."""
    return [
        file
        for file in downloads_path.iterdir()
        if 'Kontoauszug' in file.name and file.is_file()
    ]


def get_acc_files_from_gdrive_folder(folder_id: str, service: Any) -> list[DriveFile]:
    """List all files in a specified Google Drive folder."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    items: list[DriveFile] = results.get('files', [])
    if not items:
        print('No files found.')
        return []
    else:
        items = sorted(items, key=lambda x: x['name'])
        print('Files in folder:')
        for item in items:
            print(f'{item["name"]} (ID: {item["id"]})')

    return items


def check_if_file_already_processed(
    file_name: str, service: Any, regular_folder_id: str
) -> bool:
    """Check if a file with the same name already exists in the regular folder."""
    query = (
        f"'{regular_folder_id}' in parents and name = '{file_name}' and trashed = false"
    )
    results = service.files().list(q=query, fields='files(id, name)').execute()
    items = results.get('files', [])
    return len(items) > 0


def extract_text_from_pdf(file_id: str, service: Any) -> str:
    """Extract the text from a pdf file in GDrive."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_data = request.execute()

        with pdfplumber.open(BytesIO(file_data)) as pdf:
            full_pdf_text = ''
            for page in pdf.pages:
                full_pdf_text += page.extract_text(extraction_mode='layout')
        return full_pdf_text
    except Exception as e:
        logging.error(
            f'An error occurred while extracting text from PDF with ID {file_id}: {e}'
        )
        return ''


def move_file(
    file_id: str, name: str, old_folder_id: str, new_folder_id: str, service: Any
) -> None:
    """Move a file from old_folder_id to new_folder_id."""
    service.files().update(
        fileId=file_id,
        addParents=new_folder_id,
        removeParents=old_folder_id,
        body={'name': name},
        fields='id, name, parents',
    ).execute()

    print(f'File {file_id} moved to {new_folder_id}')


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


def get_balance_of_account(lines: list[str], balance_type: str) -> tuple[float, int]:
    """Get all balances (old or new) of an account."""
    results = []
    for idx, line in enumerate(lines):
        if balance_type in line:
            balance_float = extract_balance_from_line(line)
            results.append((balance_float, idx))
    if not results:
        logging.error(f'{balance_type} not found.')
        return (0.0, -1)
    else:
        if balance_type == 'neuer Kontostand':
            final_result = results[-1]
        if balance_type == 'alter Kontostand':
            final_result = results[0]
    return final_result


def get_all_transactions(
    lines: list[str], old_balance_idx: int, new_balance_idx: int
) -> list[list[str]]:
    """Extract all transactions from an account statement between two index markers."""
    transactions_part = lines[old_balance_idx + 1 : new_balance_idx]
    pattern_transaction_start = re.compile(r'\d{2}\.\d{2}\. \d{2}\.\d{2}\.')
    pattern_transaction_start_alt = re.compile(r'Übertrag')

    transactions = []
    current_transaction: list[str] = []

    for line in transactions_part:
        # If line starts with Übertrag or with pattern_transaction_start, then it is a new transaction
        if pattern_transaction_start_alt.match(line) or pattern_transaction_start.match(
            line
        ):
            transactions.append(current_transaction)
            current_transaction = []
        current_transaction.append(line)

    transactions.append(current_transaction)  # Append the last transaction

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


def get_transaction_value(transaction: list[str]) -> float:
    """Get the value of the transaction."""
    value = transaction[0].split(' ')[-2]
    value_float = float(value.replace('.', '').replace(',', '.'))

    return value_float
