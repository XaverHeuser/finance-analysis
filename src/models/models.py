"""Data models used in the extractor module."""

from dataclasses import dataclass


@dataclass
class DriveFile:
    """
    Represents a file stored in Google Drive.

    Attributes:
        id: The unique identifier of the file in Google Drive.
        name: The display name of the file.
    """

    id: str
    name: str
