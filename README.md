# my-hands-canvas

Self-hosted [OpenHands Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/) deployment for [antonockr1](https://github.com/antono4).

## What's deployed

| URL | Service |
| --- | --- |
| `https://work-1-fvvocjbmlliibebj.prod-runtime.all-hands.dev/` | Agent Canvas UI (ingress, port 12000, host work-1) |
| `https://work-2-fvvocjbmlliibebj.prod-runtime.all-hands.dev/` | Agent Canvas UI (static frontend, port 12001, host work-2) |

The stack runs:

- **Agent Server** (OpenHands SDK v1.44.x) on `127.0.0.1:19000` — chat/agent API (`/api`, `/sockets`, `/server_info`, …)
- **Automation backend** on `127.0.0.1:19001` — `/api/automation/*`
- **Ingress proxy** on port **12000** (work-host 1) — serves the prebuilt Canvas UI, routes API prefixes to the backend, and the editor under `/vscode`
- **Static frontend** on port **12001** (work-host 2) — serves the prebuilt Canvas UIand proxies API paths (including `/vscode)to the backend

Both services serve the **official prebuilt OpenHands Canvas UI** (`@openhands/agent-canvas` v1.16.0, titlethe same as [app.all-hands.dev](https://app.all-hands.dev/). The frontend auto-injects the session API key so no login is needed.

## Restart

```bash
# 1. Full backend stack (agent-server + automation + ingress on 12000)
OH_CANVAS_SAFE_BACKEND_PORT=19000 \
OH_CANVAS_SAFE_AUTOMATION_PORT=19001 \
OH_CANVAS_SAFE_STATE_DIR="$HOME/.openhands/agent-canvas" \
TMUX_TMPDIR=/tmp/agent-canvas-tmux \
  agent-canvas --port 12000 --host 0.0.0.0
```

```bash
# 2. Static UI (port 12001, shared backend)
node "$PWD/scripts/static-launch.mjs"
```

or use the bundled launcher:

```bash
./start-canvas.sh full    # backend+ingress+frontend on  ​12000
./start-canvas.sh backend # agent-server + automation + ingress on 12000
./start-canvas.sh ui      # static frontend + proxy on  ​12001
```

> Note:`TMUX_TMPDIR` must point ata writable tmpdir (defaulted by the
> launcher)so the agent-server's tmux sessions never collide with the owning shell's
> tmux socket — the collision kills the parent session and the whole stack with it.

## Notes

- The static launcher reads the session API key from `~/.openhands/agent-canvas/api-key.txt` at runtime — no secret is stored in this repository.
- LLM profiles are stored encrypted at `~/.openhands/profiles/*.json` under the user's home directoryand are decrypted with the persisted `OH_SECRET_KEY` (see `scripts/static-launch.mjs` and the launcher's `secret-key.txt`).
- The three legacy files (`index.html`, `server.py`, `work2.html`) were custom clones of the Canvas UI and are no longer needed —the official prebuilt build from `@openhands/agent-canvas` is served instead, exactly like app.all-hands.dev.