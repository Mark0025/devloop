#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# start_default.sh — one-shot helper to spin up an Ollama pod on RunPod,
# verify it responds, and print the shutdown command.
# -----------------------------------------------------------------------------
# Prerequisites:
#   • pipx installed (brew install pipx && pipx ensurepath)
#   • RUNPOD_API_KEY exported in your shell or .env
#
# Usage:
#   chmod +x runpod/start_default.sh
#   RUNPOD_API_KEY=xxxxxxxx  ./runpod/start_default.sh
# -----------------------------------------------------------------------------
set -euo pipefail

TEMPLATE_ID="ollama/ollama"           # community template (CUDA-ready)
POD_NAME="devloop-ollama"
PORT="11434"
DISK="80"

# 1. Ensure runpod CLI is installed
if ! command -v runpod &> /dev/null; then
  echo "[runpod] installing runpod via pipx"; echo
  pipx install runpod
fi

# 2. Configure API key (will create ~/.config/runpod/config.yaml)
runpod config set api_key "${RUNPOD_API_KEY:?RUNPOD_API_KEY not set}"

# 3. Launch pod if not already running
if runpod pod status --name "$POD_NAME" &>/dev/null; then
  echo "[runpod] pod '$POD_NAME' already exists, skipping launch"
else
  echo "[runpod] launching pod '$POD_NAME' from template $TEMPLATE_ID"
  runpod pod launch \
    --template-id "$TEMPLATE_ID" \
    --gpu-count 1 \
    --disk-size "$DISK" \
    --name "$POD_NAME" \
    --ports "${PORT}:http"
fi

# 4. Poll until RUNNING and obtain IP
ATTEMPTS=60
while (( ATTEMPTS-- > 0 )); do
  STATUS_JSON=$(runpod pod status --name "$POD_NAME" --json)
  STATE=$(echo "$STATUS_JSON" | jq -r '.status')
  IP=$(echo "$STATUS_JSON"   | jq -r '.endpoints[0].ip // empty')
  if [[ "$STATE" == "RUNNING" && -n "$IP" ]]; then
    echo "[runpod] pod is RUNNING → $IP"
    break
  fi
  echo "[runpod] waiting for pod… state=$STATE attempts left=$ATTEMPTS"
  sleep 10
done

if [[ "$STATE" != "RUNNING" ]]; then
  echo "[runpod] pod failed to reach RUNNING state" >&2
  exit 1
fi

# 5. Quick health check — list models
echo "[runpod] querying /api/tags"
http --check-status --timeout 30 GET "http://$IP:$PORT/api/tags"

# 6. Print shutdown hint
cat <<EOF

Success! The Ollama endpoint is live at http://$IP:$PORT

When you are done testing, stop the pod:
  runpod pod stop --name $POD_NAME
EOF
