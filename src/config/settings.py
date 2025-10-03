"""This module contains configuration settings for the application."""

import logging
import os
import sys


# from dotenv import load_dotenv # local testing only
# load_dotenv() # local testing only

SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
TEMP_FOLDER_ID = os.environ.get('TEMP_FOLDER_ID')
REGULAR_FOLDER_ID = os.environ.get('REGULAR_FOLDER_ID')


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
    )
