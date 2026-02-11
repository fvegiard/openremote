# MCP Server Reference Directory

Each subdirectory contains the SOURCE CODE of an MCP server for inspection.
These are **read-only reference copies** — the actual MCP servers run from their installed locations.

## MCP Servers

| MCP Server | Source | Purpose |
|---|---|---|
| `filesystem/` | `@anthropic/mcp-filesystem` | File system access |
| `google-cloud/` | `@anthropic/mcp-google-cloud` | Google Cloud integration |
| `memory/` | `@anthropic/mcp-memory` | Persistent memory |
| `fetch/` | `@anthropic/mcp-fetch` | HTTP fetching |
| `puppeteer/` | `@anthropic/mcp-puppeteer` | Browser automation |
| `brave-search/` | `@anthropic/mcp-brave-search` | Web search |
| `context7/` | `@context7/mcp-server` | Documentation context |

## Usage

These are for **inspection and learning** only. To understand how an MCP server works,
browse its source code here. The actual running servers are configured in your
`opencode.json` or `settings.json`.
