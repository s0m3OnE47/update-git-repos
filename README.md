# Git Repository Updater

A Python script that automates updating multiple git repositories by reading configurations from a CSV file. It fetches and pulls specified branches for each repository, with colored output and a detailed summary.

## Features

- **CSV Configuration**: Store repository paths and branches in a simple CSV file
- **Multiple Branches**: Update multiple branches per repository (comma-separated)
- **Safe Updates**: Uses `--ff-only` for pulls to avoid merge conflicts
- **Uncommitted Changes Detection**: Skips repositories with uncommitted changes
- **Colored Output**: Visual feedback with colored status messages
- **Dry Run Mode**: Preview what would be updated without making changes
- **Branch Restoration**: Automatically restores original branch after updates
- **Summary Table**: Clear overview of all update results

## Project Structure

```
update-git-repos/
├── src/
│   └── update_repos.py      # Main entry point script
├── util/
│   ├── __init__.py          # Package exports
│   ├── models.py            # Repository and UpdateResult dataclasses
│   ├── csv_handler.py       # CSV parsing utilities
│   ├── git_operations.py    # Git command wrapper (GitRepo class)
│   └── logger.py            # Colored console output
├── repos.csv                # Your repository configuration
├── install.sh               # Installation script
├── uninstall.sh             # Uninstallation script
├── README.md                # This file
├── LICENSE                  # MIT License
└── requirements.txt         # Dependencies (none required)
```

## Installation

### Quick Install

```bash
# Clone or download the project
git clone <repo-url> /opt/update-git-repos

# Run the install script
cd /opt/update-git-repos
sudo ./install.sh
```

The install script will:
1. Copy the project to `/opt/update-git-repos` (if not already there)
2. Make the main script executable
3. Create a symlink at `/usr/bin/update-git-repos`

After installation, you can run `update-git-repos` from anywhere.

### Manual Install

```bash
# Make the script executable
sudo chmod +x /opt/update-git-repos/src/update_repos.py

# Create symlink in /usr/bin
sudo ln -s /opt/update-git-repos/src/update_repos.py /usr/bin/update-git-repos
```

## Uninstallation

```bash
cd /opt/update-git-repos
sudo ./uninstall.sh
```

The uninstall script will:
1. Remove the symlink from `/usr/bin`
2. Optionally remove the project directory from `/opt`

### Manual Uninstall

```bash
# Remove the symlink
sudo rm /usr/bin/update-git-repos

# Optionally remove the project
sudo rm -rf /opt/update-git-repos
```

## Quick Start

### 1. Configure Your Repositories

Edit `repos.csv` to add your repositories:

```csv
path,branches,enabled
/home/aniket/Projects/Personal/cuda-course,master,true
/home/user/projects/webapp,"main,develop",true
/home/user/projects/api,main,true
/home/user/projects/old-project,master,false
```

### 2. Run the Script

```bash
# If installed system-wide
update-git-repos

# Or from the project directory
python src/update_repos.py

# With a custom CSV file
update-git-repos --csv /path/to/my_repos.csv

# Preview without making changes
update-git-repos --dry-run
```

## CSV File Format

| Column | Required | Description |
|--------|----------|-------------|
| `path` | Yes | Absolute path to the git repository |
| `branches` | Yes | Branch name(s) to update. Use quotes for multiple: `"main,develop,feature"` |
| `enabled` | No | Set to `false` to skip without removing from file. Defaults to `true` |

### Example CSV

```csv
path,branches,enabled
/home/user/projects/frontend,main,true
/home/user/projects/backend,"main,staging,production",true
/home/user/projects/legacy,master,false
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--csv PATH` | `-c` | Path to CSV configuration file (default: `repos.csv`) |
| `--no-color` | | Disable colored terminal output |
| `--dry-run` | `-n` | Preview repositories without updating |
| `--help` | `-h` | Show help message |

## Usage Examples

### Basic Usage

```bash
# Update all enabled repositories using default repos.csv
update-git-repos
```

### Custom CSV File

```bash
# Use a different configuration file
update-git-repos --csv ~/work/work_repos.csv
```

### Dry Run (Preview)

```bash
# See what would be updated without making changes
update-git-repos --dry-run
```

### Disable Colors (for scripts/logs)

```bash
# Plain text output without ANSI colors
update-git-repos --no-color > update.log
```

### Combine Options

```bash
# Preview updates from custom file without colors
update-git-repos --csv ~/repos.csv --dry-run --no-color
```

## Sample Output

```
──────────────────────────────────────────────────
Git Repository Updater
──────────────────────────────────────────────────
→ Loading repositories from: repos.csv

→ Processing: /home/user/projects/frontend
  Fetching remotes...
  Updating branch: main
✓     main: Updated successfully

→ Processing: /home/user/projects/backend
  Fetching remotes...
  Updating branch: main
✓     main: Updated successfully
  Updating branch: develop
✓     develop: Updated successfully

──────────────────────────────────────────────────
Update Summary
──────────────────────────────────────────────────
→ Repository  Branch   Status    Message
  ──────────────────────────────────────────────
✓ frontend    main     ✓ OK      Successfully updated 'main'
✓ backend     main     ✓ OK      Successfully updated 'main'
✓ backend     develop  ✓ OK      Successfully updated 'develop'

→ Total: 3 | Success: 3 | Failed: 0
```

## How It Works

1. **Load Configuration**: Reads the CSV file and parses repository configurations
2. **Validate Repositories**: Checks that paths exist and are valid git repositories
3. **Check for Changes**: Skips repositories with uncommitted changes
4. **Fetch Remotes**: Runs `git fetch --all --prune` to get latest refs
5. **Update Branches**: For each branch, runs `git checkout` and `git pull --ff-only`
6. **Restore Branch**: Returns to the original branch after updates
7. **Print Summary**: Shows a table of all results with success/failure status

## Safety Features

- **Fast-Forward Only**: Uses `--ff-only` for pulls to avoid creating merge commits
- **Uncommitted Changes**: Detects and skips repositories with uncommitted changes
- **Branch Restoration**: Always restores the original branch, even if errors occur
- **Timeout Protection**: Git commands have a 2-minute timeout
- **Graceful Interruption**: Handles Ctrl+C cleanly

## Extending the Script

The modular structure makes it easy to extend:

### Add New Git Operations

Edit `util/git_operations.py` to add methods to the `GitRepo` class:

```python
def stash(self) -> bool:
    """Stash uncommitted changes."""
    try:
        self._run_git("stash", "push", "-m", "auto-stash")
        return True
    except GitError:
        return False
```

### Add New CSV Columns

1. Update `Repository` dataclass in `util/models.py`
2. Update `from_csv_row()` method to parse the new column

### Add New CLI Options

Edit `parse_args()` in `src/update_repos.py`:

```python
parser.add_argument(
    "--verbose", "-v",
    action="store_true",
    help="Show detailed git output"
)
```

## Requirements

- Python 3.10 or higher (uses modern type hints)
- Git installed and available in PATH
- No external Python dependencies

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All updates successful |
| 1 | One or more updates failed |
| 130 | Interrupted by user (Ctrl+C) |

## License

MIT License - Feel free to use and modify as needed.

