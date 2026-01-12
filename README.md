# Oh-My-OpenCode (TanStack) — secure-ish “code from your phone” Docker setup

A self-hosted, **headless OpenCode server with the Oh-My-OpenCode harness**, pre-configured with the **Sisyphus orchestrator agent** and **common language servers for a TanStack app**, plus:

- **Multi-agent orchestration** (via Oh-My-OpenCode)
- **Reverse proxy with HTTP Basic Auth** (Caddy)
- Optional **web terminal** (`ttyd`)
- Optional **Cloudflare Tunnel** for public access without opening inbound ports
- Optional **web “stack manager”** (Dockge) *behind a separate auth gate* (with socket proxy for security)

> Goal: run on a home **Mac Studio** (Docker Desktop), but remain a general solution.

---

## ✅ Security principles (what this repo tries to enforce)

1. **No root in web-exposed app containers**
   - The OpenCode/Oh-My-OpenCode and web terminal containers run as a non-root user (`dev`).
   - The proxy container is also configured to run as non-root and listen on an unprivileged port.

2. **No direct container ports exposed except the proxy**
   - Only the proxy is published (or nothing is published if you use Cloudflare Tunnel).
   - The core services are on an internal Docker network only.

3. **Danger zone is opt-in**
   - Dockge (web UI to manage Docker Compose) is **disabled by default** and only enabled via a Compose profile.
   - Dockge uses a **socket-proxy** to avoid direct host-root access.

---

## Repository layout

```text
.
├── .devcontainer/
│   └── devcontainer.json
├── .env.example
├── .gitignore
├── Caddyfile
├── docker-compose.yaml
├── Dockerfile
├── README.md
└── scripts/
    └── entrypoint.sh
```

---

## Prerequisites

### Required
- Docker (Docker Desktop on macOS)
- A domain in Cloudflare (recommended if you want global access)

### Recommended
- Cloudflare Zero Trust (for **Cloudflare Tunnel** + **Cloudflare Access** MFA/SSO)
- A dedicated machine user / token strategy for your AI provider keys (don’t bake secrets into the image)

---

## 1) Clone and configure environment

```bash
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_DIR>

cp .env.example .env
```

### Generate a Caddy password hash

Caddy uses **hashed** passwords for `basic_auth`.

```bash
docker run --rm caddy:2 caddy hash-password --plaintext 'YOUR_STRONG_PASSWORD'
```

Put the result into `.env`:

```bash
BASIC_AUTH_USER=aleksei
BASIC_AUTH_HASH=$2a$14$...paste_hash_here...
```

---

## 2) Build and run locally (no Cloudflare yet)

```bash
docker compose up -d --build
```

Open in your browser:

* Proxy (auth gate): [http://localhost:8080](http://localhost:8080)
* Oh-My-OpenCode is served at `/` (defaults to **Sisyphus** agent)
* Web terminal (optional): `/term/`

Stop:

```bash
docker compose down
```

---

## 3) Set up Cloudflare Tunnel (recommended “anywhere access”)

... [rest of the file remains similar but with Oh-My-OpenCode naming] ...

### Option A (recommended): Remote-managed tunnel using a token

1. In Cloudflare dashboard:

   * Go to **Zero Trust** → **Networks** → **Tunnels**
   * Create a new tunnel (choose **cloudflared**)
   * Choose Docker as the connector method and copy the **token**

2. Put token into `.env`:

```bash
CF_TUNNEL_TOKEN=...your_token...
```

3. Start with the tunnel profile:

```bash
docker compose --profile tunnel up -d --build
```

4. In Cloudflare Zero Trust (tunnel settings), add a **Public Hostname**:

   * `hostname`: `code.yourdomain.com`
   * `service`: `http://proxy:8080`

Now you should be able to open:

* [https://code.yourdomain.com/](https://code.yourdomain.com/)

### Add Cloudflare Access (strongly recommended)

In **Zero Trust → Access → Applications**:

* Protect `code.yourdomain.com`
* Require MFA / your identity provider
* Optionally restrict by country, device posture, IP allowlist, etc.

> If you use Access, Basic Auth becomes a second layer, not your only gate.

---

## 4) Using it day-to-day

### Oh-My-OpenCode Web UI

* Go to `/` (root)
* Work inside `/workspace` (your repo is mounted there)
* Oh-My-OpenCode will use the configured language servers installed in the image.

### Web terminal (ttyd)

* Go to `/term/`
* You get a shell in the container as the non-root `dev` user.

### Running dev server / tests

From the terminal:

```bash
cd /workspace
pnpm install
pnpm dev
```

If you want to reach your app dev server from your phone, you have two approaches:

1. Add another proxy route in `Caddyfile` to forward `/app/*` to your Vite dev server port
2. Or expose the Vite port through Cloudflare separately (less ideal)

---

## 5) VS Code Dev Container support

Open the repo in VS Code and run:

* “Dev Containers: Reopen in Container”

This uses `.devcontainer/devcontainer.json` and attaches to the `devcontainer` service.

---

## 6) “Recreate/redeploy from the web” (optional, risky)

### Dockge (disabled by default)

Dockge is convenient, but it mounts `/var/run/docker.sock` which is **effectively host-admin**.

Enable it only if:

* You also protect it with **Cloudflare Access** and a separate password, and
* You understand the risk.

Start Dockge:

```bash
docker compose --profile admin up -d
```

Then open:

* http(s)://<your-host>/dockge/

**Hard rule:** do not expose Dockge publicly without Cloudflare Access + strict restrictions.

---

## Configuration notes

### Non-root containers

* OpenCode/terminal run as user `dev` from the Dockerfile.
* Proxy runs as a non-root user (see `proxy/Dockerfile`) and listens on `8080`.

### CORS

If you keep everything behind the same origin (`https://code.yourdomain.com/`), you typically don’t need custom CORS.
If you do, set:

```bash
OPENCODE_CORS=https://code.yourdomain.com
```

### Permissions for running shell commands

This repo initializes OpenCode config with:

* `"permission": { "bash": "ask" }`

That’s intentional. You can relax it later, but “ask” is safer when exposed over the internet.

---

## Troubleshooting

### “I can’t access files / permission denied”

On macOS Docker Desktop, make sure the repo folder is allowed in:

* Docker Desktop → Settings → Resources → File Sharing

### Cloudflare shows 502 / “Host error”

* Confirm `cloudflared` is on the same Docker network as `proxy`
* Confirm your Cloudflare “service” points to `http://proxy:8080`
* Check logs:

```bash
docker compose logs -f cloudflared
docker compose logs -f proxy
```

### Basic auth doesn’t work

* Confirm the hash is the output of `caddy hash-password`
* Confirm your `.env` is actually being loaded:

```bash
docker compose config | grep BASIC_AUTH -n
```

---

## Updating

Pull changes and rebuild:

```bash
git pull
docker compose up -d --build
```

---

## Security hardening ideas (recommended improvements)

If you want to make this more robust for a public GitHub repo:

1. **Prefer Cloudflare Access** over relying on Basic Auth alone.
2. **Disable the web terminal by default**

   * Keep it behind a Compose profile so users opt-in:

     * `docker compose --profile term up -d`
3. Add container hardening:

   * `security_opt: ["no-new-privileges:true"]`
   * `cap_drop: ["ALL"]`
   * `read_only: true` + `tmpfs: /tmp` (only if your app supports it)
4. Consider isolating build tooling

   * A “runner” container for compiling/testing separate from the web-exposed UI container.
5. Use an allowlist in Cloudflare Access (email domain, device posture, country, IP)
6. Add rate limiting / WAF rules in Cloudflare to reduce brute-force pressure.

---

## References (official docs)

* OpenCode CLI: [https://opencode.ai/docs/cli/](https://opencode.ai/docs/cli/)
* OpenCode Config: [https://opencode.ai/docs/config/](https://opencode.ai/docs/config/)
* OpenCode Plugins: [https://opencode.ai/docs/plugins/](https://opencode.ai/docs/plugins/)
* Oh-My-OpenCode (npm): [https://www.npmjs.com/package/oh-my-opencode](https://www.npmjs.com/package/oh-my-opencode)
* Caddy basic_auth: [https://caddyserver.com/docs/caddyfile/directives/basic_auth](https://caddyserver.com/docs/caddyfile/directives/basic_auth)
* Cloudflare Tunnel run parameters: [https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/cloudflared-parameters/run-parameters/](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/cloudflared-parameters/run-parameters/)

---

## License

Pick a license that fits your intent (MIT is common for templates).

---

# Appendix: The “non-root proxy” image (proxy/Dockerfile)

This makes sure the proxy itself does not run as root and listens on port 8080.

```dockerfile
FROM caddy:2-alpine

# Create non-root user
RUN addgroup -g 10001 caddyuser && adduser -D -H -u 10001 -G caddyuser caddyuser

# Prepare writable dirs for Caddy
RUN mkdir -p /data /config && chown -R 10001:10001 /data /config

USER 10001:10001
EXPOSE 8080

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
```

---

# Appendix: Proxy config note (Caddyfile)

Make sure your Caddyfile listens on `:8080` (unprivileged port), e.g.:

```caddyfile
:8080 {
  # ...
}
```

---

# Appendix: “What’s the threat model here?”

This stack gives you “convenient remote dev” but it is not equivalent to a locked-down enterprise remote workstation.
Assume:

* If your credentials are stolen, attackers may run code in your repo environment.
* If you enable Dockge, compromise could lead to host takeover.

Use Cloudflare Access + MFA, avoid exposing Dockge, and keep the web terminal disabled unless you truly need it.
