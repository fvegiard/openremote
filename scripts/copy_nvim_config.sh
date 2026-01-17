#!/usr/bin/env bash
# Copy local nvim config to project directory for Docker builds
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_DIR="${PROJECT_DIR}/dotfiles/nvim"

SOURCE_DIR="${HOME}/.config/nvim"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Error: Source nvim config not found at $SOURCE_DIR"
  exit 1
fi

echo "Copying nvim config from $SOURCE_DIR to $TARGET_DIR..."

# Remove old copy if exists
rm -rf "$TARGET_DIR"

# Copy config
cp -r "$SOURCE_DIR" "$TARGET_DIR"

# Remove plugin cache/state (will be reinstalled in container)
rm -rf "$TARGET_DIR/plugin"
rm -rf "$TARGET_DIR/.git"

echo "Done. Nvim config copied to $TARGET_DIR"
echo "Rebuild the container to apply: docker compose up -d --build"