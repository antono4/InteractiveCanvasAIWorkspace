#!/usr/bin/env bash
# Launcher for the self-hosted OpenHands Agent Canvas stack on the work hosts.
# Reads the session API key from the Canvas state dir at runtime; no secrets in git.
set -euo pipefail

CANVAS_BIN="${CANVAS_BIN:-$HOME/.npm-global/bin/agent-canvas}"
STATE_DIR="${OH_CANVAS_SAFE_STATE_DIR:-$HOME/.openhands/agent-canvas}"
LAUNCHER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -x "$CANVAS_BIN" ]; then
  echo "agent-canvas CLI not found at $CANVAS_BIN" >&2
  echo "Install it with: npm install -g @openhands/agent-canvas@1.16.0" >&2
  exit 1
fi
if [ ! -s "$STATE_DIR/api-key.txt" ]; then
  echo "Canvas session API key not found at $STATE_DIR/api-key.txt" >&2
  echo "Start the stack once with the official launcher to generate it." >&2
  exit 1
fi

# The agent-server launches tmux sessions for terminal tool calls. The
# parent shell runs inside its own tmux pool, so isolate the launcher's
# tmux socket in a dedicated tmpdir to avoid killing the parent session.

TMUX_TMPDIR="${TMUX_TMPDIR:-/tmp/agent-canvas-tmux}"
mkdir -p "$TMUX_TMPDIR"
export TMUX_TMPDIR

MODE="${1:-full}"
case "$MODE" in
  backend)
    # Agent-server + automation + ingress on 12000 (no frontend).
    OH_CANVAS_SAFE_BACKEND_PORT=19000 \
    OH_CANVAS_SAFE_AUTOMATION_PORT=19001 \
    OH_CANVAS_SAFE_STATE_DIR="$STATE_DIR" \
      "$CANVAS_BIN" --backend-only --port 12000 --host 0.0.0.0
    ;;
  ui)
    # Static frontend + proxy on port 12001; proxies API to the backend.

    node "$LAUNCHER_DIR/scripts/static-launch.mjs"
    ;;
  full|*)
    # Full stack: ingress 12000 (Canvas UI + API), backend 19000/19001.,

    OH_CANVAS_SAFE_BACKEND_PORT=19000 \
    OH_CANVAS_SAFE_AUTOMATION_PORT=19001 \
    OH_CANVAS_SAFE_STATE_DIR="$STATE_DIR" \
      "$CANVAS_BIN" --port 12000 --host 0.0.0.0
    ;;
esac