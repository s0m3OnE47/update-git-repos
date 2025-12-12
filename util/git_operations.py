"""
Git operations wrapper with context manager support.

This module provides a GitRepo class that wraps git commands using subprocess,
with a context manager pattern to ensure the original branch is restored after
operations complete.
"""

import subprocess
from pathlib import Path
from typing import Self

from .logger import Logger
from .models import UpdateResult


class GitError(Exception):
    """Exception raised when a git command fails."""
    pass


class GitRepo:
    """
    Context manager for git repository operations.

    Provides methods for common git operations (fetch, checkout, pull) with
    automatic restoration of the original branch when exiting the context.

    Example:
        with GitRepo(Path("/path/to/repo")) as repo:
            repo.fetch_all()
            for branch in ["main", "develop"]:
                if repo.checkout(branch):
                    repo.pull()
        # Original branch is automatically restored

    Attributes:
        path: Path to the git repository
        original_branch: Branch that was active when context was entered
    """

    def __init__(self, path: Path) -> None:
        """
        Initialize a GitRepo instance.

        Args:
            path: Path to the git repository directory
        """
        self.path = path
        self.original_branch: str | None = None
        self._entered = False

    def __enter__(self) -> Self:
        """
        Enter the context and save the current branch.

        Returns:
            Self for use in with statements
        """
        self._entered = True
        self.original_branch = self.get_current_branch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context and restore the original branch.

        Attempts to restore the original branch if it was saved.
        Logs a warning if restoration fails.
        """
        if self.original_branch:
            try:
                self._run_git("checkout", self.original_branch)
            except GitError:
                Logger.warning(f"Could not restore original branch: {self.original_branch}")

    def _run_git(self, *args: str, capture_output: bool = True) -> subprocess.CompletedProcess:
        """
        Run a git command in the repository directory.

        Args:
            *args: Git command and arguments (e.g., "fetch", "--all")
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess instance with command results

        Raises:
            GitError: If the git command fails
        """
        cmd = ["git", "-C", str(self.path)] + list(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=120  # 2 minute timeout for slow operations
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                raise GitError(f"Git command failed: {' '.join(args)}\n{error_msg}")

            return result

        except subprocess.TimeoutExpired:
            raise GitError(f"Git command timed out: {' '.join(args)}")
        except FileNotFoundError:
            raise GitError("Git is not installed or not in PATH")

    def get_current_branch(self) -> str:
        """
        Get the name of the current branch.

        Returns:
            Current branch name

        Raises:
            GitError: If unable to determine current branch
        """
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip()

    def fetch_all(self) -> bool:
        """
        Fetch all remotes.

        Returns:
            True if fetch succeeded, False otherwise
        """
        try:
            self._run_git("fetch", "--all", "--prune")
            return True
        except GitError as e:
            Logger.error(f"Fetch failed: {e}")
            return False

    def checkout(self, branch: str) -> bool:
        """
        Checkout the specified branch.

        Args:
            branch: Name of the branch to checkout

        Returns:
            True if checkout succeeded, False otherwise
        """
        try:
            self._run_git("checkout", branch)
            return True
        except GitError as e:
            Logger.error(f"Checkout failed for branch '{branch}': {e}")
            return False

    def pull(self) -> bool:
        """
        Pull latest changes from remote.

        Returns:
            True if pull succeeded, False otherwise
        """
        try:
            self._run_git("pull", "--ff-only")
            return True
        except GitError as e:
            Logger.error(f"Pull failed: {e}")
            return False

    def has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes in the repository.

        Returns:
            True if there are uncommitted changes
        """
        try:
            result = self._run_git("status", "--porcelain")
            return bool(result.stdout.strip())
        except GitError:
            return True  # Assume changes if we can't check

    def update_branch(self, branch: str) -> UpdateResult:
        """
        Update a specific branch by checking out and pulling.

        This is a convenience method that combines checkout and pull
        with appropriate error handling and result reporting.

        Args:
            branch: Name of the branch to update

        Returns:
            UpdateResult with success status and message
        """
        # Try to checkout the branch
        if not self.checkout(branch):
            return UpdateResult.failure_result(
                self.path, branch, f"Failed to checkout branch '{branch}'"
            )

        # Try to pull
        if not self.pull():
            return UpdateResult.failure_result(
                self.path, branch, f"Failed to pull branch '{branch}'"
            )

        return UpdateResult.success_result(
            self.path, branch, f"Successfully updated '{branch}'"
        )
