"""Module to handle Google authentication and setup."""

import os
from typing import Any, Optional

import google.auth
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config.google import SCOPES


def get_google_clients(
    json_credentials_path: Optional[str] = None,
) -> tuple[gspread.Client, Any]:
    """Set up Google connection. Local or Cloud Run."""
    if json_credentials_path and os.path.exists(json_credentials_path):
        # Local authentication via Service Account JSON
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
