"""Module for processing account statements."""

import logging
import os
import sys

from config.settings import REGULAR_FOLDER_ID, SPREADSHEET_ID, TEMP_FOLDER_ID
from domain.balances import get_balances_of_account
from domain.files import (
    get_year_from_file_name,
    is_valid_account_file,
    standardize_account_file_name,
)
from domain.transactions import (
    append_transaction,
    extract_transaction_info,
    get_all_transactions,
)
from infrastructure.google_auth import get_google_clients
from infrastructure.google_drive import (
    drive_file_exists,
    get_acc_files_from_gdrive,
    move_drive_file,
)
from infrastructure.google_sheets import (
    load_sheet_to_dataframe,
    open_worksheet,
    update_google_sheet,
)
from infrastructure.pdf_parser import extract_pdf_lines, extract_text_from_pdf_in_gdrive


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

# Path of creds for local testing:
# -> Add as param to get_google_clients()
# Activate local environs in config/settings.py
# Path(os.getcwd()) / 'credentials/gc-creds.json'


def process_account_statements() -> None:
    """Process all account statements in the downloads folder."""
    # Set up google clients
    client, service = get_google_clients()

    # Get all account statement files from GDrive temp folder
    acc_states = get_acc_files_from_gdrive(TEMP_FOLDER_ID, service)

    # Process each account statement file
    for acc_state in acc_states:
        # Validate file name
        if not is_valid_account_file(acc_state['name']):
            # TODO: validate account number in file name
            logging.warning(f'Skipping file {acc_state["name"]}')
            continue

        # Standardize file name
        acc_state['name'] = standardize_account_file_name(acc_state['name'])

        # Check if file already processed
        if drive_file_exists(acc_state['name'], service, REGULAR_FOLDER_ID):
            logging.info(f'File {acc_state["name"]} already processed. Skipping.')
            continue

        # Extract year from file name
        acc_state_year = get_year_from_file_name(acc_state['name'])

        # Extract text from PDF
        full_pdf_text = extract_text_from_pdf_in_gdrive(acc_state['id'], service)
        lines = extract_pdf_lines(full_pdf_text)

        # Get account balances and transactions
        old_balance_index, new_balance_index = get_balances_of_account(lines)
        all_transactions = get_all_transactions(
            lines, old_balance_index, new_balance_index
        )

        # Open Google Sheets and convert to dataframe
        sheet_transactions = open_worksheet(client, SPREADSHEET_ID, 'Transaktionen')
        df_transactions = load_sheet_to_dataframe(sheet_transactions)

        # Process each transaction
        for transaction_index in range(len(all_transactions)):
            transaction = all_transactions[transaction_index]

            # Extract transaction info
            t_name, t_value, t_type, t_date = extract_transaction_info(
                transaction, acc_state_year
            )

            # Add new row to dataframe
            append_transaction(df_transactions, t_name, t_value, t_type, t_date)

        # Update Google Sheets with new data
        update_google_sheet(sheet_transactions, df_transactions)
        logging.info('All changes saved to Google Sheets!')

        # Move processed file to regular folder
        file_id = acc_state['id']
        file_name = acc_state['name']
        move_drive_file(file_id, file_name, TEMP_FOLDER_ID, REGULAR_FOLDER_ID, service)
