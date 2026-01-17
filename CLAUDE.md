# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a self-hosted Docker setup for running OpenCode with the Oh-My-OpenCode agent harness. It provides a web-based AI coding environment with multi-agent orchestration, accessible via browser or SSH, secured behind a Caddy reverse proxy with HTTP Basic Auth and optional Cloudflare Tunnel.

## Common Commands

### Build and Run
```bash
# Start the stack (builds if needed)
docker compose up -d --build

# Start with Cloudflare Tunnel
docker compose --profile tunnel up -d --build

# Start with Dockge admin UI (security risk - read docs first)
docker compose --profile admin up -d

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
docker compose logs -f ohmyopencode # OpenCode service only
docker compose logs -f cloudflared  # Tunnel logs
docker compose logs -f proxy        # Caddy proxy logs
```

### Ralph Wiggum Autonomous Loop
```bash
# Run autonomous AI coding loop (requires PLAN.txt and RALPH_PROGRESS.txt in /workspace/project/)
./scripts/ralph.sh <iterations>
```

## Architecture

### Docker Services
- **proxy** (Caddy): Reverse proxy with Basic Auth, routes `/` to OpenCode UI, `/term/` to web terminal, `/dockge/` to admin
- **ohmyopencode**: Main OpenCode web UI server with Oh-My-OpenCode harness, runs on port 4096
- **terminal**: Web terminal (ttyd) for shell access, runs on port 7681
- **cloudflared** (profile: tunnel): Cloudflare Tunnel for public access
- **dockge** + **socket-proxy** (profile: admin): Optional Docker Compose management UI

### Key Files
- `Dockerfile`: Node.js 20 image with OpenCode, Oh-My-OpenCode, ttyd, language servers, uv, bun, spec-kit
- `scripts/entrypoint.sh`: Handles SSH setup, GitHub repo cloning, config generation, and command dispatch
- `scripts/ralph.sh`: Autonomous AI coding loop script
- `Caddyfile`: Proxy routing and auth configuration
- `opencode_config/`: User-specific OpenCode and Oh-My-OpenCode configurations (copied into container)
- `opencode_config_example/`: Example configurations showing available settings

### Network Architecture
- `edge` network: External-facing (proxy, cloudflared)
- `internal` network: Backend services communication

### User Setup
- Non-root user `dev` (UID 1000) runs all application containers
- SSH access available via `SSH_PUBLIC_KEY` environment variable
- Workspace mounted at `/workspace`, repos cloned to `/workspace/project`

## Configuration

### Environment Variables (.env)
Required:
- `BASIC_AUTH_USER` / `BASIC_AUTH_HASH`: Caddy auth credentials

Optional:
- `GITHUB_REPO_URL` / `GITHUB_TOKEN`: Auto-clone a repository on startup
- `CF_TUNNEL_TOKEN`: Cloudflare Tunnel token for public access
- `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`: Cloud LLM providers
- `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`: Local LLM (e.g., LM Studio)
- `SSH_PUBLIC_KEY`: Enable SSH access to the container

### OpenCode Configuration
- Config files in `opencode_config/` are copied to container at build
- `opencode.json`: Server settings, plugins, providers, MCP servers
- `oh-my-opencode.json`: Agent configurations and model assignments
- Default agent: Sisyphus (via Oh-My-OpenCode)
- Default permission mode: `bash: "ask"` (safer for web exposure)

## Installed Tools (in container)
- Node.js 20, npm, pnpm, bun
- Python 3 with uv
- TypeScript and language servers (TS, Tailwind, YAML, Bash, Dockerfile, GraphQL, Prisma)
- spec-kit (specify CLI) for Spec-Driven Development
- ripgrep, jq, git, SSH