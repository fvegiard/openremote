# 🧠 LENA — Plan Complet de Personnalisation et Déploiement

> **Objectif** : Transformer le fork d'`openremote` en un conteneur Docker portable
> nommé **Lena** — un environnement IA autonome, complet avec vectorisation de docs,
> prêt à migrer du laptop vers une tour ML/AI dédiée ($25K).

---

## 📦 Ce Que Le Fork Fournit Déjà (Base)

| Composant | Version | Status |
|---|---|---|
| OpenCode CLI | latest | ✅ Installé |
| Oh My OpenCode | latest (npm + bun) | ✅ Installé |
| Node.js | 24 | ✅ Base image |
| Bun | latest | ✅ Installé |
| uv (Python) | latest | ✅ Installé |
| Neovim | nightly | ✅ Installé |
| tmux + tmuxp | latest | ✅ Installé |
| LSP Servers | TS, Tailwind, YAML, Bash, Docker, GraphQL, Prisma | ✅ Installés |
| ttyd (web terminal) | 1.7.7 | ✅ Installé |
| SSH Server | OpenSSH | ✅ Configuré |
| Playwright + Chromium | latest | ✅ Installé |
| clawd.bot | latest | ✅ Installé |
| spec-kit | latest | ✅ Installé |
| Homebrew | latest | ✅ Installé |

### Agents Oh My OpenCode Pré-Configurés

| Agent | Rôle | Modèle par défaut |
|---|---|---|
| **Sisyphus** | Worker autonome (ne stop jamais) | configurable |
| **Planner-Sisyphus** | Planificateur de tâches | configurable |
| **Librarian** | Chercheur de docs/code | configurable (flash) |
| **Explore** | Exploration rapide du codebase | configurable (flash) |
| **Oracle** | Architecte / Debugger | configurable |
| **Frontend UI/UX Engineer** | Design & composants | configurable |
| **Document Writer** | Rédaction docs/specs | configurable (flash) |
| **Multimodal Looker** | Analyse d'images/screenshots | configurable (flash) |

---

## 🔧 Phase 1 — Personnalisation de la Persona (MAINTENANT)

### 1.1 Renommer `dev` → `lena`

**Fichiers à modifier :**
- [ ] `Dockerfile` : `ARG USER=dev` → `ARG USER=lena`
- [ ] `Dockerfile` : Tous les chemins `/home/dev/` → `/home/lena/`
- [ ] `docker-compose.yaml` : `dev_home` volume → `lena_home`  
- [ ] `docker-compose.yaml` : Service name `ohmyopencode` → `lena`
- [ ] `scripts/entrypoint.sh` : Référence `dev` user → `lena`
- [ ] `.env.example` : Ajouter `LENA_` prefix pour clarté

### 1.2 Configurer les Modèles IA (Persona Lena)

**Fichier :** `opencode_config/opencode.json`

```json
{
  "provider": {
    "google": {
      "models": {
        "antigravity-gemini-3-pro": { ... },
        "antigravity-gemini-3-flash": { ... }
      }
    },
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (GPU Local)",
      "options": {
        "baseURL": "http://host.docker.internal:11434/v1"
      },
      "models": {
        "qwen3-coder:latest": { "name": "Qwen3 Coder (local GPU)" },
        "qwen3-vl:32b": { "name": "Qwen3 VL 32B (local GPU)" },
        "qwen3-embedding:8b": { "name": "Qwen3 Embedding 8B (local)" }
      }
    }
  }
}
```

### 1.3 Configurer les Agents Oh My OpenCode pour Lena

**Fichier :** `opencode_config/oh-my-opencode.json`

Routing des agents vers les modèles optimaux :
- **Workers lourds** (Sisyphus, Oracle, Planner) → Gemini 3 Pro ou Qwen3 Coder local
- **Workers rapides** (Explore, Librarian) → Gemini 3 Flash ou Qwen3 Coder local
- **Multimodal** → Qwen3 VL 32B local pour analyse d'images

### 1.4 Ajouter ta Clé SSH

**Fichier :** `.env` (copié depuis `.env.example`)

```bash
SSH_PUBLIC_KEY="<contenu de ~/.ssh/id_ed25519.pub>"
GOOGLE_API_KEY="<ta clé Gemini>"
# Ollama tourne sur l'hôte, pas besoin de clé
```

---

## 🗄️ Phase 2 — Vector DB pour Documentation (ENSUITE)

### 2.1 Objectif

Intégrer dans le conteneur un serveur de vectorisation qui indexe toute la documentation
(OpenClaw, projets locaux, etc.) pour que les agents puissent chercher dedans.

### 2.2 Architecture

```
┌─ Conteneur Lena ──────────────────────────────────────┐
│                                                        │
│  OpenCode ←→ Oh My OpenCode                            │
│       ↕                                                │
│  MCP Server (vectordb)  ←→  SQLite + FAISS index       │
│       ↕                      ↕                         │
│  Ollama (via host)       Documents Markdown             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2.3 Composants à Ajouter

- [ ] `vectordb/` — Dossier Python avec un serveur MCP local
- [ ] `vectordb/requirements.txt` — `faiss-cpu`, `sqlite3`, `fastapi`, `sentence-transformers`
- [ ] `vectordb/server.py` — Serveur FastAPI exposé sur port 8765
- [ ] `vectordb/ingest.py` — Script d'ingestion Markdown → embeddings
- [ ] Ajouter la config MCP dans `opencode.json` :
  ```json
  "mcp": {
    "vectordb": {
      "type": "local",
      "command": "/opt/vectordb/.venv/bin/python",
      "args": ["/opt/vectordb/server.py"]
    }
  }
  ```
- [ ] Modifier `Dockerfile` pour installer l'env Python vectordb
- [ ] Modifier `docker-compose.yaml` pour exposer le port 8765

### 2.4 Ingestion OpenClaw

1. Scraper les docs OpenClaw → Markdown
2. Chunker les fichiers (512 tokens par chunk)
3. Embeddings via Qwen3 Embedding 8B (via Ollama sur l'hôte)
4. Stocker dans SQLite+FAISS index
5. Servir via MCP pour que les agents cherchent dedans

---

## 🚀 Phase 3 — Build, Test & Portabilité (APRÈS)

### 3.1 Build Local

```bash
cd ~/Documents/GitHub/'antigravity dev'/opencode
cp .env.example .env
# Éditer .env avec tes clés
docker compose up -d --build
```

### 3.2 Tester

```bash
# SSH dans le conteneur
ssh -p 2222 lena@localhost

# Ou via le terminal web
open http://localhost:4096

# Vérifier OpenCode
opencode --version

# Vérifier les agents
opencode /agents
```

### 3.3 Exporter pour la Tour ML/AI

```bash
# Sauvegarder l'image complète
docker save lena-ai:latest | gzip > lena-ai-backup.tar.gz

# Sur la tour ($25K) :
docker load < lena-ai-backup.tar.gz
docker compose up -d

# Accès distant depuis le laptop via Tailscale
ssh lena@<tailscale-ip>
```

### 3.4 Volumes à Persister

| Volume | Contenu | Survit au rebuild |
|---|---|---|
| `lena_home` | Config user, historique, clés | ✅ Oui |
| `./workspace` | Projets de code | ✅ Oui (bind mount) |
| FAISS index | Vector DB indexée | Via volume nommé |

---

## 📋 Phase 4 — Enrichissements Futurs (ROADMAP)

- [ ] Ajouter Tailscale VPN dans le conteneur pour accès distant
- [ ] Intégrer GitHub Actions pour CI/CD automatique
- [ ] Ajouter monitoring (Prometheus/Grafana) pour la santé du conteneur
- [ ] Configurer les notifications Slack via webhook (Ralph agent)
- [ ] Multi-GPU support quand la tour arrive
- [ ] Ajouter plus de Language Servers (Python via Pyright, Go via gopls, Rust via rust-analyzer)

---

## 🎯 Résumé des Actions Immédiates

| # | Action | Fichier(s) | Effort |
|---|---|---|---|
| 1 | Renommer `dev` → `lena` | Dockerfile, compose, entrypoint | 10 min |
| 2 | Créer `opencode_config/` depuis examples | Config dir | 5 min |
| 3 | Configurer Ollama local comme provider | opencode.json | 5 min |
| 4 | Router agents vers bons modèles | oh-my-opencode.json | 5 min |
| 5 | Créer `.env` avec tes vraies clés | .env | 2 min |
| 6 | Build & test le conteneur | Terminal | 15 min |
| 7 | Push le fork personnalisé sur GitHub | Git | 2 min |

**Total estimé Phase 1 : ~45 minutes**

---

*Ce plan est un document vivant. Chaque phase sera exécutée séquentiellement
après validation. La Phase 2 (Vector DB) sera ajoutée au Dockerfile une fois
la Phase 1 validée et fonctionnelle.*
