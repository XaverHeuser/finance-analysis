"""Utility functions for local storage operations."""

from pathlib import Path


def get_all_acc_states_from_local_storage(local_path: Path) -> list[Path]:
    """Get all the account statement files from the downloads folder."""
    return [
        file
        for file in local_path.iterdir()
        if 'Kontoauszug' in file.name and file.is_file()
    ]
