"""This file processes an account statement and writes the data into a GSheet."""

import logging
import os
from pathlib import Path
import sys

import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.utils.data_extracting import (
    extract_text_from_pdf,
    get_all_account_statement_files,
    get_all_transactions,
    get_balance_of_account,
)
from src.utils.data_loading import update_google_sheet
from src.utils.data_transforming import add_new_row, extract_transaction_info
from src.utils.google_connection import set_up_google_connection


##############
# Configs
##############
credentials_path = Path('../credentials/cool-plasma-452619-v4-feb20b70d461.json')
downloads_path = Path.home() / 'Downloads'

client, service = set_up_google_connection(credentials_path)
SPREADSHEET_ID = '1OnrW1foE-1lOtgfxBv2Y5qqJSDnW4hiYeLpScjgFKxM'


def process_account_statements():
    """Process all account statements in the downloads folder."""
    ###############
    # Get files
    ###############
    acc_files = get_all_account_statement_files(downloads_path)

    for acc_file in acc_files:
        # TODO: Check if file already in GDrive folder

        full_pdf_text = extract_text_from_pdf(acc_file)
        lines = full_pdf_text.split('\n')

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

        ####################
        # Open Spreadsheet
        ####################
        spreadsheet = client.open_by_key(SPREADSHEET_ID)  # TODO: Put in secrets/env

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
        logging.info('All changes saved to Google Sheets!')


if __name__ == '__main__':
    process_account_statements()
