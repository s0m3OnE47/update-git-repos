"""
CSV file parsing utilities for repository configuration.

This module provides functions to load and parse repository configurations
from CSV files using a generator pattern for memory efficiency.
"""

import csv
from pathlib import Path
from typing import Generator

from .models import Repository
from .logger import Logger


def load_repositories(csv_path: Path) -> Generator[Repository, None, None]:
    """
    Load repositories from a CSV file.

    Yields Repository objects for each valid row, skipping invalid rows
    with warnings logged to console.

    Expected CSV format:
        path,branches,enabled
        /path/to/repo,main,true
        /path/to/repo2,"main,develop",true

    Args:
        csv_path: Path to the CSV configuration file

    Yields:
        Repository objects for each valid, enabled row

    Raises:
        FileNotFoundError: If the CSV file does not exist
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    if not csv_path.is_file():
        raise ValueError(f"Path is not a file: {csv_path}")

    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Validate headers
        if reader.fieldnames is None:
            Logger.error("CSV file is empty or has no headers")
            return

        required_fields = {"path", "branches"}
        missing_fields = required_fields - set(reader.fieldnames)
        if missing_fields:
            Logger.error(f"CSV missing required columns: {', '.join(missing_fields)}")
            return

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                repo = Repository.from_csv_row(row)
                yield repo
            except ValueError as e:
                Logger.warning(f"Row {row_num}: {e}")
                continue


def get_enabled_repositories(csv_path: Path) -> Generator[Repository, None, None]:
    """
    Load only enabled repositories from a CSV file.

    Convenience wrapper around load_repositories that filters out
    disabled repositories and validates each one.

    Args:
        csv_path: Path to the CSV configuration file

    Yields:
        Valid, enabled Repository objects
    """
    for repo in load_repositories(csv_path):
        if not repo.enabled:
            Logger.dim(f"  Skipping disabled repository: {repo.path}")
            continue

        # Validate the repository
        errors = repo.validate()
        if errors:
            for error in errors:
                Logger.warning(error)
            continue

        yield repo


def count_repositories(csv_path: Path) -> tuple[int, int]:
    """
    Count total and enabled repositories in a CSV file.

    Args:
        csv_path: Path to the CSV configuration file

    Returns:
        Tuple of (total_count, enabled_count)
    """
    total = 0
    enabled = 0

    for repo in load_repositories(csv_path):
        total += 1
        if repo.enabled and not repo.validate():
            enabled += 1

    return total, enabled
