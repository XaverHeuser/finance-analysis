"""This module includes functions for loading data into Google Sheets."""

import pandas as pd

from gspread import Worksheet
from gspread_dataframe import set_with_dataframe


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
