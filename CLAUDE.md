# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a self-hosted Docker setup for running OpenCode with the Oh-My-OpenCode agent harness. It provides an **SSH-only** dev environment (no web UI), with the ability to expose Vite dev server frontend via Caddy reverse proxy with HTTP Basic Auth. Optional Cloudflare Tunnel for remote access.

## Common Commands

### Build and Run
```bash
# Start the stack (builds if needed)
docker compose up -d --build

# Start with Cloudflare Tunnel
docker compose --profile tunnel up -d --build

# Stop the stack
docker compose down
```

### Generate Caddy Password Hash
```bash
docker run --rm caddy:2 caddy hash-password --plaintext 'YOUR_PASSWORD'
```

### View Logs
```bash
docker compose logs -f              # All services
docker compose logs -f ohmyopencode # Dev container only
docker compose logs -f cloudflared  # Tunnel logs
docker compose logs -f proxy        # Caddy proxy logs
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
- **proxy** (Caddy): Reverse proxy with Basic Auth, routes `/` to Vite dev server (port 5173)
- **ohmyopencode**: Dev container with SSH access, runs tools and Vite dev server
- **cloudflared** (profile: tunnel): Cloudflare Tunnel for public access

### Key Files
- `Dockerfile`: Node.js 20 image with OpenCode, Oh-My-OpenCode, language servers, uv, bun, spec-kit
- `scripts/entrypoint.sh`: Handles SSH setup, GitHub repo cloning, config generation, and command dispatch
- `scripts/ralph.sh`: Autonomous AI coding loop script
- `Caddyfile`: Proxy routing and auth configuration for Vite frontend
- `opencode_config/`: User-specific OpenCode and Oh-My-OpenCode configurations (copied into container)
- `opencode_config_example/`: Example configurations showing available settings

### Network Architecture
- `edge` network: External-facing (proxy, cloudflared)
- `internal` network: Backend services communication

### User Setup
- Non-root user `dev` (UID 1000) runs all application containers
- SSH access via `SSH_PUBLIC_KEY` environment variable (required)
- Workspace mounted at `/workspace`, repos cloned to `/workspace/project`

## Configuration

### Environment Variables (.env)
Required:
- `BASIC_AUTH_USER` / `BASIC_AUTH_HASH`: Caddy auth credentials for Vite frontend
- `SSH_PUBLIC_KEY`: SSH public key for container access

Optional:
- `GITHUB_REPO_URL` / `GITHUB_TOKEN`: Auto-clone a repository on startup
- `CF_TUNNEL_TOKEN`: Cloudflare Tunnel token for public access
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
