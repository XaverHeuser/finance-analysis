"""This module contains file-related utility functions."""

import logging


def standardize_account_file_name(file_name: str) -> str | None:
    """Standardize the account statement file name."""
    try:
        # Cut off after the 4th underscore
        new_name = '_'.join(file_name.split('_')[:4])
        if not new_name.lower().endswith('.pdf'):
            new_name += '.pdf'
        return new_name
    except Exception as e:
        logging.error(f'Error standardizing file name {file_name}: {e}')
        return None


def is_valid_account_file(file_name: str) -> bool:
    """Check if the file name matches the expected pattern for account statements."""
    file_name_lower = file_name.lower()
    return 'kontoauszug' in file_name_lower and file_name_lower.endswith('.pdf')


def get_year_from_file_name(file_name: str) -> str | None:
    """Extract the year from the standardized account statement file name."""
    try:
        year = file_name.split('_')[1]
        logging.info(f'Extracted year {year} from file name {file_name}')
        return year
    except IndexError as e:
        logging.error(f'Error extracting year from file name {file_name}: {e}')
        return None
    except Exception as e:
        logging.error(f'Unexpected error extracting year from {file_name}: {e}')
        return None
