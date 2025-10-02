"""Module for Google Drive file operations."""

import logging
from typing import Any

from models.models import DriveFile


def drive_file_exists(file_name: str, service: Any, regular_folder_id: str) -> bool:
    """Check if a file with the same name already exists in the regular folder."""
    query = (
        f"'{regular_folder_id}' in parents and name = '{file_name}' and trashed = false"
    )
    results = service.files().list(q=query, fields='files(id, name)').execute()
    items = results.get('files', [])
    return len(items) > 0


def move_drive_file(
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
    logging.info(f'File {file_id} moved to {new_folder_id}')


def get_acc_files_from_gdrive(folder_id: str, service: Any) -> list[DriveFile]:
    """List all files in a specified Google Drive folder."""
    try:
        # Build query to fetch all files inside the folder (not trashed)
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields='files(id, name)').execute()
        items: list[DriveFile] = results.get('files', [])

        if not items:
            logging.warning('No files found.')
            return []

        # Sort files alphabetically by name
        items = sorted(items, key=lambda x: x['name'])

        # Print files for debugging/informational purposes
        logging.info(f'Found {len(items)} files in folder {folder_id}')
        for item in items:
            logging.debug(f'File: {item["name"]} (ID: {item["id"]})')

        return items

    except Exception as e:
        logging.error(
            f'An error occurred while fetching files from folder {folder_id}: {e}'
        )
        return []
