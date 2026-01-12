#!/usr/bin/env bash
set -euo pipefail

# Defaults
: "${OPENCODE_HOST:=0.0.0.0}"
: "${OPENCODE_PORT:=4096}"
: "${OPENCODE_CORS:=}"           # comma-separated list, e.g. "https://your.domain,https://another.domain"
: "${OPENCODE_WORKDIR:=/workspace}"

# Prevent "open browser" attempts in headless environments
export BROWSER="${BROWSER:-/usr/bin/true}"

CONFIG_DIR="${HOME}/.config/opencode"
CONFIG_FILE="${CONFIG_DIR}/opencode.json"

mkdir -p "${CONFIG_DIR}"
mkdir -p "${OPENCODE_WORKDIR}"

# Clone repo if GITHUB_REPO_URL is set
if [[ -n "${GITHUB_REPO_URL:-}" ]]; then
  # Remove any potential Windows carriage returns
  GITHUB_REPO_URL=$(echo "${GITHUB_REPO_URL}" | tr -d '\r')
  
  echo "Checking GitHub repository: ${GITHUB_REPO_URL}"
  ls -la "${OPENCODE_WORKDIR}" || true
  
  # Clone into a fixed directory 'project' so we can gitignore it easily
  TARGET_DIR="${OPENCODE_WORKDIR}/project"
  
  if [[ -d "${TARGET_DIR}" ]]; then
    echo "Directory ${TARGET_DIR} already exists. Skipping clone."
  else
    echo "Cloning into ${TARGET_DIR}..."
    
    # Construct URL with token if provided
    CLONE_URL="${GITHUB_REPO_URL}"
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
       GITHUB_TOKEN=$(echo "${GITHUB_TOKEN}" | tr -d '\r')
       # Insert token into URL: https://TOKEN@github.com/user/repo.git
       # Remove https://
       CLEAN_URL="${GITHUB_REPO_URL#https://}"
       CLONE_URL="https://${GITHUB_TOKEN}@${CLEAN_URL}"
    fi
    
    # Try cloning; if it fails, check if it's because it exists (race condition or weird FS state)
    git clone "${CLONE_URL}" "${TARGET_DIR}" || {
      if [[ -d "${TARGET_DIR}" ]]; then
        echo "Clone returned error but directory exists. Continuing."
      else
        echo "Git clone failed."
        exit 1
      fi
    }
  fi
fi

cors_json="[]"
cors_flags=()
if [[ -n "${OPENCODE_CORS}" ]]; then
  # turn "a,b,c" into ["a","b","c"]
  IFS=',' read -ra parts <<< "${OPENCODE_CORS}"
  cors_json="$(printf '%s\n' "${parts[@]}" | jq -R . | jq -s .)"
  for origin in "${parts[@]}"; do
    cors_flags+=(--cors "$origin")
  done
fi

# Write a minimal config once (server + plugin + safer default permissions)
# OpenCode supports configuring server settings in config. :contentReference[oaicite:0]{index=0}
if [[ ! -f "${CONFIG_FILE}" ]]; then
  cat > "${CONFIG_FILE}" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "server": {
    "hostname": "${OPENCODE_HOST}",
    "port": ${OPENCODE_PORT},
    "mdns": false,
    "cors": ${cors_json}
  },
  "plugin": ["oh-my-opencode"],
  "default_agent": "sisyphus",
  "permission": {
    "bash": "ask"
  }
}
EOF
fi

cd "${OPENCODE_WORKDIR}"
# If a repo was specified and exists (cloned above), enter it so IDE opens it as root
if [[ -n "${GITHUB_REPO_URL:-}" ]]; then
   TARGET_DIR="${OPENCODE_WORKDIR}/project"
   if [[ -d "${TARGET_DIR}" ]]; then
      echo "Entering ${TARGET_DIR}..."
      cd "${TARGET_DIR}"
   fi
fi

case "${1:-}" in
  opencode-web|web)
    shift || true
    exec opencode web --hostname "${OPENCODE_HOST}" --port "${OPENCODE_PORT}" "${cors_flags[@]}" "$@"
    ;;
  opencode-serve|serve)
    shift || true
    exec opencode serve --hostname "${OPENCODE_HOST}" --port "${OPENCODE_PORT}" "${cors_flags[@]}" "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
