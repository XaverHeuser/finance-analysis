"""This module includes functions for transforming data."""

from datetime import date
import logging

import pandas as pd

from utils.data_extracting import check_income_or_expense, get_transaction_value


def extract_transaction_info(
    transaction: list[str], transaction_year: str
) -> tuple[str, pd.DataFrame, str, float, str]:
    """Return transaction type, DataFrame, name, value, and month."""
    logging.info(f'Checking transaction {transaction}...')

    transaction_name = transaction[1].strip()
    transaction_value = get_transaction_value(transaction)
    transaction_type = check_income_or_expense(transaction)

    date_str = str(transaction[0].split(' ')[0] + transaction_year)
    transaction_date = pd.to_datetime(date_str, format='%d.%m.%Y').date()

    return transaction_name, transaction_value, transaction_type, transaction_date


def add_new_row(
    df: pd.DataFrame, t_name: str, t_value: float, t_type: str, t_date: date
) -> None:
    """Append a new row to the DataFrame."""
    # Append new row to DataFrame
    df.loc[len(df)] = [t_name, t_value, t_type, t_date, None, None]
