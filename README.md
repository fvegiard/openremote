# Lena — Autonomous AI Development Container

> OpenCode + Oh My OpenCode + Ollama (local GPU) — portable, secure, ready to deploy.

A self-hosted Docker setup for running **OpenCode with Oh My OpenCode multi-agent harness**, personalized as **Lena** — an autonomous AI development environment.

## Features

- 🧠 **Multi-agent AI orchestration** via Oh My OpenCode (Sisyphus, Oracle, Librarian, etc.)
- 🚀 **Dual LLM providers**: Gemini 3 Pro/Flash (cloud) + Ollama RTX 5090 (local GPU)
- 👁️ **Multimodal vision** via Qwen3 VL 32B on local GPU
- 🔒 **SSH access** to dev container with full coding toolchain (tmux, Neovim, Bun, uv)
- 🌐 **Web UI** via OpenCode web interface (port 4096)
- 🔌 **Vite dev server** exposed directly (port 5173)
- 📦 **Portable**: `docker save` → move to any machine → `docker load`
- 🛡️ Designed for **Tailscale VPN** secure remote access

> **Goal**: Run on a home PC/laptop with GPU, connect from anywhere via SSH through Tailscale VPN.
> When a dedicated ML tower arrives, `docker save/load` and it's identical.

---

## Quick Start

### 1) Clone and configure
```bash
git clone https://github.com/fvegiard/openremote.git lena
cd lena
cp .env.example .env
# Edit .env with your SSH key and API keys
```

### 2) Build and run
```bash
docker compose up -d --build
```

### 3) Connect
```bash
# SSH into the container
ssh -p 2222 lena@localhost

# Or open the web UI
open http://localhost:4096
```

---

## Agent Architecture

| Agent | Role | Model | Speed |
|---|---|---|---|
| **Sisyphus** | Autonomous worker — never stops | Gemini 3 Pro | 🐢 Deep |
| **Planner-Sisyphus** | Strategic task decomposition | Gemini 3 Pro | 🐢 Deep |
| **Oracle** | Architect & root-cause debugger | Gemini 3 Pro | 🐢 Deep |
| **Frontend UI/UX** | Premium interface specialist | Gemini 3 Pro | 🐢 Deep |
| **Librarian** | Doc & code search | Gemini 3 Flash | ⚡ Fast |
| **Explore** | Rapid codebase understanding | Gemini 3 Flash | ⚡ Fast |
| **Document Writer** | Specs, READMEs, docs | Gemini 3 Flash | ⚡ Fast |
| **Multimodal Looker** | Vision: screenshots & diagrams | Qwen3 VL 32B (local GPU) | 🖥️ Local |

---

## Exposed Ports

| Port | Service | Purpose |
|------|---------|---------|
| 2222 | SSH | Terminal access |
| 4096 | OpenCode | Web UI |
| 5173 | Vite | Dev server (`pnpm dev --host 0.0.0.0`) |

---

## Portability

```bash
# Export the full container image
docker save lena:latest | gzip > lena-backup.tar.gz

# On the target machine
docker load < lena-backup.tar.gz
docker compose up -d
```

---

## Credits

Based on [openremote](https://github.com/aleksei-s-popov/openremote) by Aleksei Popov.
Powered by [OpenCode](https://opencode.ai) and [Oh My OpenCode](https://github.com/code-yeongyu/oh-my-opencode).
