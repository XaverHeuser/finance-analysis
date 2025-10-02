"""Module for balance extraction and processing."""

import logging


def extract_balance_from_line(line: str) -> float:
    """Extract the balance from a line of text."""
    try:
        # Get the balance and convert to float
        balance_str = line.split()[-2]
        balance_str = balance_str.replace('.', '').replace(',', '.')
        return float(balance_str)

    except (IndexError, ValueError) as e:
        logging.error(
            f'An error occurred when trying to extract the balance of a line: {line}. Fehler: {e}'
        )
        return 0.0

    except Exception as e:
        logging.error(f'Unexpected error in extract_balance_from_line: {e}')
        return 0.0


def get_balance_of_account(lines: list[str], balance_type: str) -> tuple[float, int]:
    """Get all balances (old or new) of an account."""
    try:
        results = []
        for idx, line in enumerate(lines):
            if balance_type in line:
                # Extract numeric balance from line
                balance_float = extract_balance_from_line(line)
                results.append((balance_float, idx))

        if not results:
            logging.error(f'{balance_type} not found.')
            return (0.0, -1)

        if balance_type == 'neuer Kontostand':
            return results[-1]
        if balance_type == 'alter Kontostand':
            return results[0]
        else:
            return results[0]

    except Exception as e:
        logging.error(f'Error getting balance of account ({balance_type}): {e}')
        return (0.0, -1)


def get_balances_of_account(lines: list[str]) -> tuple[int, int]:
    """Get both old and new balances of an account."""
    try:
        old_balance, old_balance_index = get_balance_of_account(
            lines, 'alter Kontostand'
        )
        new_balance, new_balance_index = get_balance_of_account(
            lines, 'neuer Kontostand'
        )
        logging.info(f'Old balance: {old_balance}€, Index: {old_balance_index}')
        logging.info(f'New balance: {new_balance}€, Index: {new_balance_index}')
        return old_balance_index, new_balance_index
    except Exception as e:
        logging.error(f'Error getting both balances of account: {e}')
        return (-1, -1)
