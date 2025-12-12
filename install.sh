#!/bin/bash
#
# Install script for Git Repository Updater
#
# This script will:
# 1. Copy the project to /opt/update-git-repos (if not already there)
# 2. Make the main script executable
# 3. Create a symlink in /usr/bin for system-wide access
#
# Usage: sudo ./install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

INSTALL_DIR="/opt/update-git-repos"
SCRIPT_PATH="$INSTALL_DIR/src/update_repos.py"
SYMLINK_PATH="/usr/bin/update-git-repos"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run as root (sudo ./install.sh)${NC}"
    exit 1
fi

echo -e "${GREEN}Installing Git Repository Updater...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If not already in /opt/update-git-repos, copy the project there
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    # Check if destination already exists (reinstall scenario)
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/src/update_repos.py" ]; then
        echo -e "${YELLOW}Existing installation found at $INSTALL_DIR${NC}"
        
        # Backup user's repos.csv to /tmp (outside install dir to survive cp -rT)
        BACKUP_FILE=""
        if [ -f "$INSTALL_DIR/repos.csv" ]; then
            echo -e "${YELLOW}Backing up existing repos.csv...${NC}"
            BACKUP_FILE="/tmp/repos.csv.backup.$$"
            cp "$INSTALL_DIR/repos.csv" "$BACKUP_FILE"
            echo -e "${GREEN}✓ Backed up to temporary location${NC}"
        fi
        
        echo -e "${YELLOW}Updating installation...${NC}"
    else
        echo -e "${YELLOW}Copying project to $INSTALL_DIR...${NC}"
        # Create directory if it doesn't exist
        mkdir -p "$INSTALL_DIR"
        BACKUP_FILE=""
    fi

    # Copy all files (using -rT to copy contents directly, works with existing dirs)
    cp -rT "$SCRIPT_DIR" "$INSTALL_DIR"
    
    # Restore user's repos.csv if backup exists
    if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        mv "$BACKUP_FILE" "$INSTALL_DIR/repos.csv"
        echo -e "${GREEN}✓ Restored user's repos.csv${NC}"
    fi

    echo -e "${GREEN}✓ Project installed to $INSTALL_DIR${NC}"
else
    echo -e "${GREEN}✓ Project already in $INSTALL_DIR${NC}"
fi

# Make the main script executable
echo -e "${YELLOW}Making script executable...${NC}"
chmod +x "$SCRIPT_PATH"
echo -e "${GREEN}✓ Made $SCRIPT_PATH executable${NC}"

# Remove existing file/symlink if it exists
if [ -e "$SYMLINK_PATH" ] || [ -L "$SYMLINK_PATH" ]; then
    if [ -L "$SYMLINK_PATH" ]; then
        echo -e "${YELLOW}Removing existing symlink...${NC}"
    else
        echo -e "${YELLOW}Removing existing file at $SYMLINK_PATH...${NC}"
    fi
    rm -f "$SYMLINK_PATH"
fi

# Create symlink in /usr/bin
echo -e "${YELLOW}Creating symlink in /usr/bin...${NC}"
ln -s "$SCRIPT_PATH" "$SYMLINK_PATH"
echo -e "${GREEN}✓ Created symlink: $SYMLINK_PATH -> $SCRIPT_PATH${NC}"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "You can now run the updater from anywhere:"
echo "  update-git-repos              # Update all repos in repos.csv"
echo "  update-git-repos --dry-run    # Preview without changes"
echo "  update-git-repos --help       # Show all options"
echo ""
echo "Configure your repositories in: $INSTALL_DIR/repos.csv"

