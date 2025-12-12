#!/bin/bash
#
# Uninstall script for Git Repository Updater
#
# This script will:
# 1. Remove the symlink from /usr/bin
# 2. Optionally remove the project from /opt/update-git-repos
#
# Usage: sudo ./uninstall.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

INSTALL_DIR="/opt/update-git-repos"
SYMLINK_PATH="/usr/bin/update-git-repos"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run as root (sudo ./uninstall.sh)${NC}"
    exit 1
fi

echo -e "${YELLOW}Uninstalling Git Repository Updater...${NC}"

# Remove symlink
if [ -L "$SYMLINK_PATH" ]; then
    rm "$SYMLINK_PATH"
    echo -e "${GREEN}✓ Removed symlink: $SYMLINK_PATH${NC}"
else
    echo -e "${YELLOW}Symlink not found: $SYMLINK_PATH${NC}"
fi

# Ask about removing the project directory
echo ""
read -p "Remove project directory $INSTALL_DIR? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓ Removed $INSTALL_DIR${NC}"
else
    echo -e "${YELLOW}Kept $INSTALL_DIR${NC}"
fi

echo ""
echo -e "${GREEN}Uninstall complete!${NC}"

