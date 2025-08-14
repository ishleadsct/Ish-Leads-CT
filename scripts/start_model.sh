#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$ROOT/models.json"
BIN="$ROOT/llama.cpp/build/bin/llama-server"

if [ ! -x "$BIN" ]; then
    echo "llama-server binary not found at $BIN"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: $0 <model_name_or_role>"
    exit 2
fi

TARGET="$1"

# Resolve by name first, then by role
NAME=$(jq -r "map(select(.name==\"$TARGET\"))[0].name // empty" "$CFG")
if [ -z "$NAME" ]; then
    NAME=$(jq -r "map(select(.role==\"$TARGET\"))[0].name // empty" "$CFG")
fi
if [ -z "$NAME" ]; then
    echo "Model not found for: $TARGET"
    exit 3
fi

PATH_TARGET=$(jq -r "map(select(.name==\"$NAME\"))[0].path" "$CFG")
PORT=$(jq -r "map(select(.name==\"$NAME\"))[0].port" "$CFG")
THREADS=$(jq -r "map(select(.name==\"$NAME\"))[0].threads" "$CFG")
CTX=$(jq -r "map(select(.name==\"$NAME\"))[0].context" "$CFG")

if [ ! -f "$PATH_TARGET" ]; then
    echo "Model file missing: $PATH_TARGET"
    exit 4
fi

# If already running, skip
if lsof -i :"$PORT" >/dev/null 2>&1; then
    echo "Already running: $NAME on port $PORT"
    exit 0
fi

LOG="$ROOT/${NAME// /_}.log"
echo "Starting $NAME on :$PORT ..."
nohup "$BIN" -m "$PATH_TARGET" --host 127.0.0.1 --port "$PORT" --ctx-size "$CTX" --threads "$THREADS" --mlock=false --embedding=false --no-mmap=false > "$LOG" 2>&1 &
echo $! > "$ROOT/${NAME// /_}.pid"
echo "OK"
