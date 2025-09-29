"""This file processes an account statement and writes the data into a GSheet."""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from utils.data_extracting import (
    check_if_file_already_processed,
    extract_text_from_pdf,
    get_acc_files_from_gdrive_folder,
    get_all_transactions,
    get_balance_of_account,
    move_file,
)
from utils.data_loading import update_google_sheet
from utils.data_transforming import add_new_row, extract_transaction_info
from utils.google_connection import set_up_google_connection


# TODO: Add comments
# TODO: Clean up code

##############
# Configs
##############
credentials_path = Path('./credentials/cool-plasma-452619-v4-feb20b70d461.json')
downloads_path = Path.home() / 'Downloads'

client, service = set_up_google_connection(credentials_path)

load_dotenv()
TEMP_FOLDER_ID = os.getenv('TEMP_FOLDER_ID')
REGULAR_FOLDER_ID = os.getenv('REGULAR_FOLDER_ID')


def process_account_statements() -> None:
    """Process all account statements in the downloads folder."""
    ###############
    # Get files
    ###############
    # acc_files = get_all_account_statement_files(downloads_path)
    acc_files = get_acc_files_from_gdrive_folder(TEMP_FOLDER_ID, service)

    for acc_file in acc_files:
        if 'Kontoauszug' not in acc_file['name']:
            print(f'Skipping file {acc_file["name"]} as it does not match criteria.')
            continue

        # Rename file
        new_name = '_'.join(acc_file['name'].split('_')[:4])
        if not new_name.lower().endswith('.pdf'):
            new_name += '.pdf'

        acc_file['name'] = new_name

        # Check if file already processed
        if check_if_file_already_processed(
            acc_file['name'], service, REGULAR_FOLDER_ID
        ):
            print(f'File {acc_file["name"]} already processed. Skipping.')
            continue

        # Get spreadsheet ID from env
        acc_file_year = acc_file['name'].split('_')[1]
        gsheet_file = f'SPREADSHEET_ID_{acc_file_year}'
        spreadsheet_id = os.getenv(gsheet_file)
        if spreadsheet_id is None:
            print(f'No spreadsheet ID found for year {acc_file_year}. Skipping file.')
            continue
        print(f'Processing file {acc_file["name"]} into spreadsheet {spreadsheet_id}.')

        # Process file
        full_pdf_text = extract_text_from_pdf(acc_file['id'], service)
        lines = full_pdf_text.split('\n')
        print(f'Extracted {len(lines)} lines from PDF.')

        acc_balance_old = get_balance_of_account(lines, 'alter Kontostand')
        acc_balance_new = get_balance_of_account(lines, 'neuer Kontostand')
        print(
            f'Old acc value, Value: {acc_balance_old[0]}€ - Line-Index: {acc_balance_old[1]}'
        )
        print(
            f'New acc value, Value: {acc_balance_new[0]}€ - Line-Index: {acc_balance_new[1]}'
        )
        all_transactions = get_all_transactions(
            lines, acc_balance_old[1], acc_balance_new[1]
        )
        print(f'Count of transactions: {len(all_transactions)}')

        ####################
        # Open Spreadsheet
        ####################
        spreadsheet = client.open_by_key(spreadsheet_id)

        sheet_incomes = spreadsheet.worksheet('Einnahmen')
        sheet_expenses = spreadsheet.worksheet('Ausgaben')

        #########################
        # Convert sheet to pdf
        #########################
        df_expenses = pd.DataFrame(sheet_expenses.get_all_values())
        df_incomes = pd.DataFrame(sheet_incomes.get_all_values())

        df_expenses.columns = df_expenses.iloc[0]
        df_expenses = df_expenses[1:].reset_index(drop=True)

        df_incomes.columns = df_incomes.iloc[0]
        df_incomes = df_incomes[1:].reset_index(drop=True)

        gsheets = {'Expense': df_expenses, 'Income': df_incomes}

        ############################################
        # Get transaction info and write into  df
        ############################################
        for transaction_index in range(len(all_transactions)):
            transaction = all_transactions[transaction_index]

            transaction_type, df, name, transaction_value, month = (
                extract_transaction_info(transaction, gsheets)
            )

            add_new_row(
                df,
                name,
                month,
                transaction_value,
                transaction_type,
                gsheets,
                general_account=True,
            )

        #############################
        # Write new data to gsheet
        #############################
        update_google_sheet(sheet_expenses, gsheets['Expense'])
        update_google_sheet(sheet_incomes, gsheets['Income'])
        print('All changes saved to Google Sheets!')

        # Move processed file to regular folder
        file_id = acc_file['id']
        move_file(file_id, acc_file['name'], TEMP_FOLDER_ID, REGULAR_FOLDER_ID, service)


if __name__ == '__main__':
    process_account_statements()
