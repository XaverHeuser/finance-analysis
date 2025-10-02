"""This module contains configuration settings for the application."""

import os


# from dotenv import load_dotenv # local testing only

# load_dotenv() # local testing only

SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
TEMP_FOLDER_ID = os.environ.get('TEMP_FOLDER_ID')
REGULAR_FOLDER_ID = os.environ.get('REGULAR_FOLDER_ID')
