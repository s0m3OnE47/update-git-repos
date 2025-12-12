"""
Data models for the Git Repository Updater.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Repository:
    """Represents a git repository configuration from CSV."""
    path: Path
    branches: list[str]
    enabled: bool = True


@dataclass
class UpdateResult:
    """Represents the result of updating a single branch."""
    repo_path: Path
    branch: str
    success: bool
    message: str

