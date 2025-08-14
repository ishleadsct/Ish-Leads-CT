#!/data/data/com.termux/files/usr/bin/bash
# Ultra AI Installer for Termux
# Installs dependencies, builds llama.cpp, and downloads models interactively.

set -e

# Paths
MODELS_DIR="/storage/emulated/0/AI_Models/.ultra_ai/models"
CONFIG_FILE="models.json"
MANIFEST="installed_models.json"

echo "=============================="
echo " Ultra AI - One-Time Installer"
echo "=============================="
echo

# 1. Ensure target directories exist
echo "[*] Creating model directory at $MODELS_DIR ..."
mkdir -p "$MODELS_DIR"

# 2. Install Termux packages
echo "[*] Installing Termux dependencies..."
pkg update -y
pkg install -y git cmake clang python curl jq

# 3. Install Python dependencies
echo "[*] Installing Python packages..."
pip install --break-system-packages aiohttp

# 4. Build llama.cpp
if [ ! -d "llama.cpp" ]; then
    echo "[*] Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git
else
    echo "[*] llama.cpp folder exists, skipping clone."
fi

cd llama.cpp
echo "[*] Building llama.cpp for aarch64..."
cmake -B build -S .
cmake --build build -j$(nproc)
cd ..

# 5. Read models.json and prompt downloads
echo "[*] Reading $CONFIG_FILE..."
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: $CONFIG_FILE not found in current directory."
    exit 1
fi

# Prepare manifest
echo "[]" > "$MANIFEST"

MODEL_COUNT=$(jq length "$CONFIG_FILE")

for i in $(seq 0 $(($MODEL_COUNT - 1))); do
    NAME=$(jq -r ".[$i].name" "$CONFIG_FILE")
    PATH_TARGET=$(jq -r ".[$i].path" "$CONFIG_FILE")
    ROLE=$(jq -r ".[$i].role" "$CONFIG_FILE")

    echo
    echo "Model: $NAME ($ROLE)"
    echo "Target: $PATH_TARGET"

    # Skip if file exists
    if [ -f "$PATH_TARGET" ]; then
        echo "[SKIP] File already exists."
        jq ". + [{\"name\":\"$NAME\",\"path\":\"$PATH_TARGET\",\"status\":\"exists\"}]" "$MANIFEST" > tmp.json && mv tmp.json "$MANIFEST"
        continue
    fi

    # Ask user if they want to download
    read -p "Download this model? (Y/n): " yn
    yn=${yn:-Y}
    if [[ ! "$yn" =~ ^[Yy]$ ]]; then
        echo "[SKIP] User chose not to download."
        jq ". + [{\"name\":\"$NAME\",\"path\":\"$PATH_TARGET\",\"status\":\"skipped\"}]" "$MANIFEST" > tmp.json && mv tmp.json "$MANIFEST"
        continue
    fi

    # Check free space
    AVAIL_MB=$(df "$MODELS_DIR" | awk 'NR==2 {print int($4/1024)}')
    echo "[INFO] Available space: ${AVAIL_MB}MB"
    if [ "$AVAIL_MB" -lt 2000 ]; then
        echo "[WARN] Less than 2GB free. Large models may fail."
        read -p "Continue anyway? (y/N): " cont
        if [[ ! "$cont" =~ ^[Yy]$ ]]; then
            echo "[SKIP] Due to low space."
            continue
        fi
    fi

    # Define download URL based on model name
    case "$NAME" in
        "Meta-Llama-3-8B-Instruct")
            URL="https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
            ;;
        "Qwen2-1.5B-Instruct")
            URL="https://huggingface.co/bartowski/Qwen2-1.5B-Instruct-GGUF/resolve/main/Qwen2-1.5B-Instruct.Q4_K_M.gguf"
            ;;
        "Qwen2-7B-Instruct")
            URL="https://huggingface.co/bartowski/Qwen2-7B-Instruct-GGUF/resolve/main/Qwen2-7B-Instruct.Q4_K_M.gguf"
            ;;
        "mistral-7b-instruct-v0.2")
            URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
            ;;
        "zephyr-7b-beta")
            URL="https://huggingface.co/TheBloke/zephyr-7b-beta-GGUF/resolve/main/zephyr-7b-beta.Q4_K_M.gguf"
            ;;
        "Phi-3-mini-4k-instruct")
            URL="https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct.Q4_K_M.gguf"
            ;;
        "DeepSeek-Coder-V2-Lite-Instruct")
            URL="https://huggingface.co/bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF/resolve/main/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"
            ;;
        "stable-code-3b")
            URL="https://huggingface.co/bartowski/stable-code-3b-GGUF/resolve/main/stable-code-3b.Q4_K_M.gguf"
            ;;
        "CodeLlama-7B-Instruct")
            URL="https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/CodeLlama-7B-Instruct.Q4_K_M.gguf"
            ;;
        *)
            echo "No download URL configured for $NAME"
            continue
            ;;
    esac

    # Download
    echo "[*] Downloading $NAME ..."
    mkdir -p "$(dirname "$PATH_TARGET")"
    curl -L "$URL" -o "$PATH_TARGET"

    if [ -f "$PATH_TARGET" ]; then
        echo "[OK] Downloaded: $PATH_TARGET"
        jq ". + [{\"name\":\"$NAME\",\"path\":\"$PATH_TARGET\",\"status\":\"downloaded\"}]" "$MANIFEST" > tmp.json && mv tmp.json "$MANIFEST"
    else
        echo "[FAIL] Download failed for $NAME"
    fi
done

echo
echo "=============================="
echo "[DONE] Installation complete!"
echo "Manifest saved to $MANIFEST"
echo "You can start Ultra AI with: ./scripts/start_all.sh"
echo "=============================="
