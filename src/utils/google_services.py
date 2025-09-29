"""This module includes code for the google services."""

from pathlib import Path
from typing import Any

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


def check_if_file_in_folder(
    file_name: str, service: Any, regular_folder_id: str
) -> bool:
    """Check if a file with the same name already exists in the regular folder."""
    query = (
        f"'{regular_folder_id}' in parents and name = '{file_name}' and trashed = false"
    )
    results = service.files().list(q=query, fields='files(id, name)').execute()
    items = results.get('files', [])
    return len(items) > 0


def move_file(
    file_id: str, name: str, old_folder_id: str, new_folder_id: str, service: Any
) -> None:
    """Move a file from old_folder_id to new_folder_id."""
    service.files().update(
        fileId=file_id,
        addParents=new_folder_id,
        removeParents=old_folder_id,
        body={'name': name},
        fields='id, name, parents',
    ).execute()

    print(f'File {file_id} moved to {new_folder_id}')
