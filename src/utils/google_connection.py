"""This module includes code for the google services."""

from pathlib import Path
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials


SCOPE_GOOGLE_DRIVE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
]


def set_up_google_connection(credentials_path: Path) -> tuple[gspread.Client, object]:
    """Set up the Google connection using service account credentials."""
    if credentials_path is None:
        raise ValueError('Credential path is required')

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_path, SCOPE_GOOGLE_DRIVE
    )
    client = gspread.authorize(creds)
    service = build('drive', 'v3', credentials=creds)

    return client, service
