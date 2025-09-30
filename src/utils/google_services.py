"""This module includes code for the google services."""

import os
from typing import Any, Optional

import google.auth
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets',
]


def set_up_google_connection(json_credentials_path: Optional[str] = None) -> tuple[gspread.Client, Any]:
    """Set up Google connection. Local or Cloud Run."""
    if json_credentials_path and os.path.exists(json_credentials_path):
        # Lokale Authentifizierung über Service Account JSON
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            json_credentials_path, SCOPES
        )
        client = gspread.authorize(creds)
        service = build('drive', 'v3', credentials=creds)
        print('Using local JSON credentials')
    else:
        # Cloud Run / Docker: default credentials
        creds, _ = google.auth.default(scopes=SCOPES)
        client = gspread.authorize(creds)
        service = build('drive', 'v3', credentials=creds)
        print('Using default Cloud Run credentials')

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
