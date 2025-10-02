"""Module for updating Google Sheets with pandas DataFrames."""

import gspread
from gspread import Worksheet
from gspread_dataframe import set_with_dataframe
import pandas as pd


def open_worksheet(
    client: gspread.Client, spreadsheet_id: str, worksheet_name: str
) -> Worksheet:
    """Open a specific worksheet in a Google Sheet."""
    spreadsheet = client.open_by_key(spreadsheet_id)
    sheet = spreadsheet.worksheet(worksheet_name)
    return sheet


def load_sheet_to_dataframe(worksheet: Worksheet) -> pd.DataFrame:
    """Load a Google Sheet into a pandas DataFrame."""
    df_transactions = pd.DataFrame(worksheet.get_all_values())
    df_transactions.columns = df_transactions.iloc[0]
    df_transactions = df_transactions[1:].reset_index(drop=True)
    return df_transactions


def update_google_sheet(sheet: Worksheet, df: pd.DataFrame) -> None:
    """Write a DataFrame to a Google Sheet while preserving header formatting."""
    set_with_dataframe(
        sheet,
        df,
        row=2,  # Start writing from row 2
        col=1,  # Start at column A
        include_index=False,
        include_column_header=False,  # Preserve row 1 (do not overwrite headers)
        resize=False,  # Preserve sheet formatting
    )
