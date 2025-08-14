#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Start Gatekeeper and Librarian first
"$ROOT/scripts/start_model.sh" gatekeeper || true
"$ROOT/scripts/start_model.sh" librarian || true

# Start backend orchestrator (aiohttp)
if ! lsof -i :8765 >/dev/null 2>&1; then
    ( cd "$ROOT/backend" && nohup python main.py > "$ROOT/backend_http.log" 2>&1 & echo $! > "$ROOT/backend_http.pid" )
fi

# Start static frontend on port 8080
if ! lsof -i :8080 >/dev/null 2>&1; then
    ( cd "$ROOT/frontend" && nohup python -m http.server 8080 > "$ROOT/frontend.log" 2>&1 & echo $! > "$ROOT/frontend.pid" )
fi

echo "Ultra AI started:"
echo "UI:  http://127.0.0.1:8080"
echo "API: http://127.0.0.1:8765"
