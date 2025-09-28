"""This module includes functions for transforming data."""

import logging

import pandas as pd

from utils.data_extracting import check_income_or_expense, get_transaction_value


def extract_transaction_info(
    transaction: list[str], gsheets: dict[str, pd.DataFrame]
) -> tuple[str, pd.DataFrame, str, float, str]:
    """Return transaction type, DataFrame, name, value, and month."""
    logging.info(f'Checking transaction {transaction}...')

    transaction_type = check_income_or_expense(transaction)

    if transaction_type not in gsheets:
        raise ValueError(f'Unknown transaction type: {transaction_type}')

    df = gsheets[transaction_type]
    transaction_value = get_transaction_value(transaction)
    name = transaction[1].strip() if len(transaction) > 1 else 'Monatsabschluss Bank'
    month = transaction[0].split('.')[1]

    return transaction_type, df, name, transaction_value, month


def add_new_row(
    df: pd.DataFrame,
    name: str,
    month: str,
    transaction_value: float,
    transaction_type: str,
    sheets: dict[str, pd.DataFrame],
    general_account: bool = False,
) -> None:
    """Add a new transaction row to the DataFrame."""
    new_row_data = [name] + [None] * (len(df.columns) - 1)
    new_row = pd.DataFrame([new_row_data], columns=df.columns)

    df = pd.concat([df, new_row], ignore_index=True)
    new_row_index = df.index[-1]

    df.loc[new_row_index, month] = transaction_value

    if transaction_type == 'Expense':
        sheets['Expense'] = df
    else:
        sheets['Income'] = df
