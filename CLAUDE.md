# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a self-hosted Docker setup for running OpenCode with the Oh-My-OpenCode agent harness. SSH-only dev environment with Vite dev server exposed directly. Designed for use behind Tailscale VPN for secure remote access.

## Common Commands

### Build and Run
```bash
# Start the stack (builds if needed)
docker compose up -d --build

# Stop the stack
docker compose down
```

### View Logs
```bash
docker compose logs -f              # All services
docker compose logs -f ohmyopencode # Dev container only
```

### SSH Access
```bash
ssh -p 2222 dev@localhost           # Local SSH access
```

### Ralph Wiggum Autonomous Loop
```bash
# Run autonomous AI coding loop (requires PLAN.txt and RALPH_PROGRESS.txt in /workspace/project/)
./scripts/ralph.sh <iterations>
```

## Architecture

### Docker Services
- **ohmyopencode**: Dev container with SSH access, runs tools and Vite dev server

### Key Files
- `Dockerfile`: Node.js 20 image with OpenCode, Oh-My-OpenCode, language servers, uv, bun, spec-kit
- `scripts/entrypoint.sh`: Handles SSH setup, GitHub repo cloning, config generation, and command dispatch
- `scripts/ralph.sh`: Autonomous AI coding loop script
- `opencode_config/`: User-specific OpenCode and Oh-My-OpenCode configurations (copied into container)
- `opencode_config_example/`: Example configurations showing available settings

### Network Architecture
Uses Docker's default bridge network. Ports exposed directly to host for access via Tailscale VPN.

### User Setup
- Non-root user `dev` (UID 1000) runs all application containers
- SSH access via `SSH_PUBLIC_KEY` environment variable (required)
- Workspace mounted at `/workspace`, repos cloned to `/workspace/project`

## Configuration

### Environment Variables (.env)
Required:
- `SSH_PUBLIC_KEY`: SSH public key for container access

Optional:
- `GITHUB_REPO_URL` / `GITHUB_TOKEN`: Auto-clone a repository on startup
- `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`: Cloud LLM providers
- `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`: Local LLM (e.g., LM Studio)

### OpenCode Configuration
- Config files in `opencode_config/` are copied to container at build
- `opencode.json`: Server settings, plugins, providers, MCP servers
- `oh-my-opencode.json`: Agent configurations and model assignments
- Default agent: Sisyphus (via Oh-My-OpenCode)

## Installed Tools (in container)
- Node.js 20, npm, pnpm, bun
- Python 3 with uv
- TypeScript and language servers (TS, Tailwind, YAML, Bash, Dockerfile, GraphQL, Prisma)
- spec-kit (specify CLI) for Spec-Driven Development
- ripgrep, jq, git, SSH

## Exposed Ports

| Port | Service | Purpose |
|------|---------|---------|
| 2222 | SSH | Terminal access |
| 5173 | Vite | Dev server |
| 4096 | OpenCode | Web UI (optional) |
