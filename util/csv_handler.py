"""
CSV file parsing utilities.
"""

from pathlib import Path
from typing import Generator

from .models import Repository


def load_repositories(csv_path: Path) -> Generator[Repository, None, None]:
    """
    Load repositories from a CSV file.
    
    Yields Repository objects, skipping invalid rows with warnings.
    """
    yield from []

