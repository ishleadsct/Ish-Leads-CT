#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$ROOT/models.json"

if [ -z "$1" ]; then
    echo "Usage: $0 <model_name_or_role>"
    exit 2
fi

TARGET="$1"

# Resolve name
NAME=$(jq -r "map(select(.name==\"$TARGET\"))[0].name // empty" "$CFG")
if [ -z "$NAME" ]; then
    NAME=$(jq -r "map(select(.role==\"$TARGET\"))[0].name // empty" "$CFG")
fi
if [ -z "$NAME" ]; then
    echo "Model not found for: $TARGET"
    exit 3
fi

PORT=$(jq -r "map(select(.name==\"$NAME\"))[0].port" "$CFG")

# Kill by PID file if exists
PIDFILE="$ROOT/${NAME// /_}.pid"
if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
    rm -f "$PIDFILE"
fi

# Fallback: kill any process on the port
if lsof -i :"$PORT" >/dev/null 2>&1; then
    PID=$(lsof -ti :"$PORT" || true)
    [ -n "$PID" ] && kill "$PID" 2>/dev/null || true
fi

echo "Stopped $NAME"
