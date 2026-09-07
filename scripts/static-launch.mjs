import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import path from 'node:path';

const home = homedir();
const pkgRoot = path.join(home, '.npm-global', 'lib', 'node_modules', '@openhands', 'agent-canvas');

// Read the persisted session API key (same file the backend launcher generated)
const key = readFileSync(path.join(home, '.openhands', 'agent-canvas', 'api-key.txt'), 'utf8').trim();

// Runtime-services info JSON for --runtime-services-info
const runtimeInfo = {
  mode: 'agent-canvas',
  agent_host_alias: 'localhost',
  services: {
    agent_server: {
      description:
        'The OpenHands Agent Server this agent is running inside. Tool calls (terminal, file_editor, browser, etc.) execute here.',
      url_from_agent: 'http://localhost:19000',
    },
    ingress: {
      description:
        'Unified entry point. Routes /api/automation/*to the automation backend, /api/*and /sockets to the agent-server, and /*to the frontend.',
      url_from_agent: 'http://localhost:12000',
    },
  },
};

const vscodePort = Number(process.env.OH_CANVAS_SAFE_VSCODE_PORT || '20000');

// ESLint-comment: the template uses `bin` in some variants; keep simple and spawn node directly.
const script = path.join(pkgRoot, 'scripts', 'static-server.mjs');
const args = [
  script,
  '--dir', path.join(pkgRoot, 'build'),
  '--port', '12001',
  '--host', '0.0.0.0',
  '--session-api-key', key,
  '--runtime-services-info', JSON.stringify(runtimeInfo),
  '--vscode-base-path', '/vscode',
  '--no-referrer-prefix', '/vscode',
  '--route', '/api=http://127.0.0.1:19000',
  '--route', '/sockets=http://127.0.0.1:19000',
  '--route', '/server_info=http://127.0.0.1:19000',
  '--route', '/docs=http://127.0.0.1:19000',
  '--route', '/redoc=http://127.0.0.1:19000',
  '--route', '/openapi.json=http://127.0.0.1:19000',
  '--route', '/alive=http://127.0.0.1:19000',
  '--route', '/health=http://127.0.0.1:19000',
  '--route', '/ready=http://127.0.0.1:19000',
  '--route', '/api/automation=http://127.0.0.1:19001',
  '--route', `/vscode=http://127.0.0.1:${vscodePort}`,
];

const child = spawn(process.execPath, args, {
  stdio: 'inherit',
  cwd: pkgRoot,
});
child.on('error', (err) => { console.error('launch error', err); process.exit(1); });
process.on('SIGTERM', () => child.kill('SIGTERM'));
process.on('SIGINT', () => child.kill('SIGINT'));