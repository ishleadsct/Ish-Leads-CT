#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Stop backend and frontend
for f in backend_http.pid frontend.pid; do
    [ -f "$ROOT/$f" ] && kill "$(cat "$ROOT/$f")" 2>/dev/null || true
    rm -f "$ROOT/$f"
done

# Stop all specialists individually (stop_model.sh doesn't take "specialist" role directly)
for model in $(jq -r '.[] | select(.role=="specialist") | .name' "$ROOT/models.json"); do
    "$ROOT/scripts/stop_model.sh" "$model" || true
done

# Stop librarian and gatekeeper
"$ROOT/scripts/stop_model.sh" librarian || true
"$ROOT/scripts/stop_model.sh" gatekeeper || true

# Clean any leftover socket files
rm -f /data/data/com.termux/files/usr/tmp/ultra_ai.sock 2>/dev/null || true

echo "Ultra AI stopped."
