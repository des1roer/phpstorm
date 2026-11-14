#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8765}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/tools/gen_update_plugins.py" --dir "$ROOT" --base-url "http://localhost:$PORT" --out "$ROOT/updatePlugins.local.xml" "$@"
echo "Plugin repository: http://localhost:$PORT/updatePlugins.local.xml"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT"
