"""This file processes an account statement and writes the data into a GSheet."""

import logging
import os
import sys

import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from utils.data_extracting import (
    extract_text_from_pdf,
    get_acc_files_from_gdrive_folder,
    get_all_transactions,
    get_balance_of_account,
)
from utils.data_loading import update_google_sheet
from utils.data_transforming import add_new_row, extract_transaction_info
from utils.google_services import (
    check_if_file_in_folder,
    move_file,
    set_up_google_connection,
)


#########################
# Configs and Variables
#########################
# client, service = set_up_google_connection(
#     Path(os.getcwd()) / 'credentials/gc-creds.json'
# ) # Local
client, service = set_up_google_connection()  # Cloud Run / Docker

# load_dotenv() # Local
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
TEMP_FOLDER_ID = os.environ.get('TEMP_FOLDER_ID')
REGULAR_FOLDER_ID = os.environ.get('REGULAR_FOLDER_ID')


#############
# Main func
#############
def process_account_statements() -> None:
    """Process all account statements in the downloads folder."""
    # Get all account statement files from GDrive temp folder
    acc_states = get_acc_files_from_gdrive_folder(TEMP_FOLDER_ID, service)

    # Process each account statement file
    for acc_state in acc_states:
        # Check if file matches criteria
        if 'Kontoauszug' not in acc_state['name']:
            logging.warning(
                f'Skipping file {acc_state["name"]} as it does not match criteria.'
            )
            continue

        # Standardize file name
        new_name = '_'.join(acc_state['name'].split('_')[:4])
        if not new_name.lower().endswith('.pdf'):
            new_name += '.pdf'
        acc_state['name'] = new_name

        # Check if file already processed
        if check_if_file_in_folder(acc_state['name'], service, REGULAR_FOLDER_ID):
            logging.info(f'File {acc_state["name"]} already processed. Skipping.')
            continue

        # Get spreadsheet ID based on year in file name
        acc_state_year = acc_state['name'].split('_')[1]

        # Extract text from PDF
        full_pdf_text = extract_text_from_pdf(acc_state['id'], service)
        lines = full_pdf_text.split('\n')
        logging.info(f'Extracted {len(lines)} lines from PDF.')

        # Get account balances and transactions
        acc_balance_old = get_balance_of_account(lines, 'alter Kontostand')
        acc_balance_new = get_balance_of_account(lines, 'neuer Kontostand')
        logging.info(
            f'Old acc value, Value: {acc_balance_old[0]}€ - Line-Index: {acc_balance_old[1]}'
        )
        logging.info(
            f'New acc value, Value: {acc_balance_new[0]}€ - Line-Index: {acc_balance_new[1]}'
        )
        all_transactions = get_all_transactions(
            lines, acc_balance_old[1], acc_balance_new[1]
        )
        logging.info(f'Count of transactions: {len(all_transactions)}')

        # Open Google Sheets
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet_transactions = spreadsheet.worksheet('Transaktionen')

        # Load existing data from Google Sheets into DataFrames
        df_sheet_transactions = pd.DataFrame(sheet_transactions.get_all_values())
        df_sheet_transactions.columns = df_sheet_transactions.iloc[0]
        df_sheet_transactions = df_sheet_transactions[1:].reset_index(drop=True)

        # Process each transaction
        for t_index in range(len(all_transactions)):
            transaction = all_transactions[t_index]

            # Extract transaction info
            t_name, t_value, t_type, t_date = extract_transaction_info(
                transaction=transaction, transaction_year=acc_state_year
            )

            # Add new row to dataframe
            add_new_row(df_sheet_transactions, t_name, t_value, t_type, t_date)

        # Update Google Sheets with new data
        update_google_sheet(sheet_transactions, df_sheet_transactions)
        logging.info('All changes saved to Google Sheets!')

        # Move processed file to regular folder
        file_id = acc_state['id']
        file_name = acc_state['name']
        move_file(file_id, file_name, TEMP_FOLDER_ID, REGULAR_FOLDER_ID, service)


if __name__ == '__main__':
    process_account_statements()
