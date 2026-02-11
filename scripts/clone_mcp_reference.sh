#!/bin/bash
# Clone MCP server source code for inspection (reference only)
# This script downloads the source code of each MCP server so the user
# can inspect how they work. These are NOT used for execution.

set -e

MCP_DIR="$(dirname "$0")/../mcp_reference"
mkdir -p "$MCP_DIR"

echo "📦 Cloning MCP server source code for inspection..."

# Context7 (from OpenCode config)
if [ ! -d "$MCP_DIR/context7" ]; then
  echo "  → context7..."
  git clone --depth 1 https://github.com/context7/mcp-server.git "$MCP_DIR/context7" 2>/dev/null || echo "  ⚠ context7 clone failed"
fi

# Filesystem MCP
if [ ! -d "$MCP_DIR/filesystem" ]; then
  echo "  → filesystem..."
  npx -y @anthropic/create-mcp-server@latest --help >/dev/null 2>&1 || true
  git clone --depth 1 https://github.com/anthropics/anthropic-quickstarts.git /tmp/anthropic-mcp 2>/dev/null || true
  if [ -d /tmp/anthropic-mcp ]; then
    cp -r /tmp/anthropic-mcp "$MCP_DIR/anthropic-mcp-reference"
    rm -rf /tmp/anthropic-mcp
  fi
fi

# Brave Search MCP
if [ ! -d "$MCP_DIR/brave-search" ]; then
  echo "  → brave-search..."
  git clone --depth 1 https://github.com/anthropics/mcp-servers.git /tmp/mcp-servers 2>/dev/null || true
  if [ -d /tmp/mcp-servers ]; then
    cp -r /tmp/mcp-servers "$MCP_DIR/mcp-servers-reference"
    rm -rf /tmp/mcp-servers
  fi
fi

echo "✅ MCP reference code downloaded to $MCP_DIR"
echo "📖 Browse the directories to inspect each MCP server's source code."
