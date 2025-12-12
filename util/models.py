"""
Data models for the Git Repository Updater.

This module contains dataclasses that represent:
- Repository: Configuration for a git repository from CSV
- UpdateResult: Result of updating a single branch
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Self


@dataclass
class Repository:
    """
    Represents a git repository configuration from CSV.

    Attributes:
        path: Absolute path to the git repository directory
        branches: List of branch names to update
        enabled: Whether this repository should be processed
    """
    path: Path
    branches: list[str] = field(default_factory=list)
    enabled: bool = True

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> Self:
        """
        Create a Repository from a CSV row dictionary.

        Args:
            row: Dictionary with 'path', 'branches', and optionally 'enabled' keys

        Returns:
            Repository instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if "path" not in row:
            raise ValueError("CSV row missing required 'path' field")

        path = Path(row["path"].strip())

        # Parse branches (comma-separated)
        branches_str = row.get("branches", "").strip()
        branches = [b.strip() for b in branches_str.split(",") if b.strip()]

        # Parse enabled flag (defaults to True)
        enabled_str = row.get("enabled", "true").strip().lower()
        enabled = enabled_str in ("true", "yes", "1", "")

        return cls(path=path, branches=branches, enabled=enabled)

    def validate(self) -> list[str]:
        """
        Validate the repository configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.path.exists():
            errors.append(f"Repository path does not exist: {self.path}")
        elif not self.path.is_dir():
            errors.append(f"Repository path is not a directory: {self.path}")
        elif not (self.path / ".git").exists():
            errors.append(f"Path is not a git repository: {self.path}")

        if not self.branches:
            errors.append(f"No branches specified for repository: {self.path}")

        return errors


@dataclass
class UpdateResult:
    """
    Represents the result of updating a single branch.

    Attributes:
        repo_path: Path to the repository that was updated
        branch: Name of the branch that was updated
        success: Whether the update was successful
        message: Human-readable status message
    """
    repo_path: Path
    branch: str
    success: bool
    message: str

    @classmethod
    def success_result(cls, repo_path: Path, branch: str, message: str = "Updated successfully") -> Self:
        """Create a successful update result."""
        return cls(repo_path=repo_path, branch=branch, success=True, message=message)

    @classmethod
    def failure_result(cls, repo_path: Path, branch: str, message: str) -> Self:
        """Create a failed update result."""
        return cls(repo_path=repo_path, branch=branch, success=False, message=message)
