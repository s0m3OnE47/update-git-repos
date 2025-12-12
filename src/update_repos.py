#!/usr/bin/env python3
"""
Git Repository Updater - Main entry point.

This script reads repository configurations from a CSV file and updates
each repository by fetching and pulling the specified branches.

Usage:
    python update_repos.py [--csv PATH] [--no-color] [--dry-run]

Examples:
    python update_repos.py                    # Use default repos.csv
    python update_repos.py --csv my_repos.csv # Use custom CSV file
    python update_repos.py --dry-run          # Preview without changes
"""

import argparse
import sys
from pathlib import Path

# Resolve symlinks to get the real script location, then find project root
# This works both for direct execution and when symlinked from /usr/bin
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add project root to path for imports
sys.path.insert(0, str(PROJECT_ROOT))

from util.models import Repository, UpdateResult
from util.logger import Logger
from util.csv_handler import get_enabled_repositories
from util.git_operations import GitRepo


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Update multiple git repositories from a CSV configuration file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV File Format:
    path,branches,enabled
    /path/to/repo,main,true
    /path/to/repo2,"main,develop",true
    /path/to/repo3,master,false

Examples:
    %(prog)s                          # Use default repos.csv
    %(prog)s --csv ~/my_repos.csv     # Custom CSV file
    %(prog)s --dry-run                # Preview without updating
        """
    )

    parser.add_argument(
        "--csv", "-c",
        type=Path,
        default=PROJECT_ROOT / "repos.csv",
        help="Path to the CSV configuration file (default: repos.csv in project root)"
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )

    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview repositories without updating"
    )

    return parser.parse_args()


def print_summary(results: list[UpdateResult]) -> None:
    """Print a formatted summary table of update results."""
    if not results:
        Logger.warning("No repositories were processed")
        return

    # Calculate column widths
    path_width = max(len(str(r.repo_path.name)) for r in results)
    branch_width = max(len(r.branch) for r in results)

    # Ensure minimum widths
    path_width = max(path_width, 10)
    branch_width = max(branch_width, 8)

    # Print header
    Logger.header("Update Summary")

    header = f"{'Repository':<{path_width}}  {'Branch':<{branch_width}}  {'Status':<8}  Message"
    separator = "─" * len(header)

    Logger.info(header)
    Logger.dim(separator)

    # Print results
    success_count = 0
    failure_count = 0

    for result in results:
        repo_name = result.repo_path.name
        status = "✓ OK" if result.success else "✗ FAIL"

        line = f"{repo_name:<{path_width}}  {result.branch:<{branch_width}}  {status:<8}  {result.message}"

        if result.success:
            Logger.success(line)
            success_count += 1
        else:
            Logger.error(line)
            failure_count += 1

    # Print totals
    Logger.newline()
    total = len(results)
    Logger.info(f"Total: {total} | Success: {success_count} | Failed: {failure_count}")


def update_repository(repo: Repository, dry_run: bool = False) -> list[UpdateResult]:
    """
    Update a single repository.

    Args:
        repo: Repository configuration
        dry_run: If True, only preview without making changes

    Returns:
        List of UpdateResult for each branch
    """
    results = []

    Logger.info(f"Processing: {repo.path}")

    if dry_run:
        for branch in repo.branches:
            Logger.dim(f"  Would update branch: {branch}")
            results.append(UpdateResult.success_result(
                repo.path, branch, "[DRY RUN] Would update"
            ))
        return results

    with GitRepo(repo.path) as git:
        # Check for uncommitted changes
        if git.has_uncommitted_changes():
            Logger.warning(f"  Repository has uncommitted changes, skipping")
            for branch in repo.branches:
                results.append(UpdateResult.failure_result(
                    repo.path, branch, "Uncommitted changes present"
                ))
            return results

        # Fetch all remotes first
        Logger.dim(f"  Fetching remotes...")
        if not git.fetch_all():
            for branch in repo.branches:
                results.append(UpdateResult.failure_result(
                    repo.path, branch, "Failed to fetch remotes"
                ))
            return results

        # Update each branch
        for branch in repo.branches:
            Logger.dim(f"  Updating branch: {branch}")
            result = git.update_branch(branch)
            results.append(result)

            if result.success:
                Logger.success(f"    {branch}: Updated successfully")
            else:
                Logger.error(f"    {branch}: {result.message}")

    return results


def main() -> int:
    """Main entry point for the repository updater."""
    args = parse_args()

    # Configure logger
    if args.no_color:
        Logger.use_colors = False

    # Print header
    Logger.header("Git Repository Updater")

    # Check CSV file
    if not args.csv.exists():
        Logger.error(f"CSV file not found: {args.csv}")
        Logger.info("Create a repos.csv file with the following format:")
        Logger.dim("  path,branches,enabled")
        Logger.dim("  /path/to/repo,main,true")
        return 1

    if args.dry_run:
        Logger.warning("DRY RUN MODE - No changes will be made")

    Logger.info(f"Loading repositories from: {args.csv}")
    Logger.newline()

    # Process repositories
    all_results: list[UpdateResult] = []
    repo_count = 0

    try:
        for repo in get_enabled_repositories(args.csv):
            repo_count += 1
            results = update_repository(repo, dry_run=args.dry_run)
            all_results.extend(results)
            Logger.newline()
    except FileNotFoundError as e:
        Logger.error(str(e))
        return 1
    except KeyboardInterrupt:
        Logger.warning("\nInterrupted by user")
        return 130

    if repo_count == 0:
        Logger.warning("No enabled repositories found in CSV file")
        return 0

    # Print summary
    print_summary(all_results)

    # Return exit code based on results
    failures = sum(1 for r in all_results if not r.success)
    return 1 if failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
