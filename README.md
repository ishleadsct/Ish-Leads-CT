Ultra AI
A mobile-first, local AI stack for Android/Termux that runs multiple GGUF models with llama.cpp. It uses a Gatekeeper → Librarian → Specialist flow to balance speed, accuracy, and device resources. One-command install, one-command start/stop, and a simple web UI.

Features

Local-only inference via llama.cpp (no cloud tokens needed)

Multi-model orchestration:

Gatekeeper (primary chat/answerer)

Librarian (quick research/summary)

Specialists (on-demand, domain-aware, with fallbacks)

Resource-aware start/stop to fit mobile RAM/CPU

Web UI with “Dive deeper?” confirmation and offline fallback

Simple scripts to start/stop everything

Requirements

Android phone with Termux (64-bit, e.g., Samsung Galaxy S24 Ultra)

Stable internet to download models (first time only)

Free storage:

Minimum 8–12 GB recommended if you download multiple models

You can choose which models to download during install

Quick Start (Termux)

Install prerequisites
pkg update -y && pkg upgrade -y
pkg install git -y

Clone the repo
git clone https://github.com/YOUR_USER/YOUR_REPO.git
cd YOUR_REPO

Make scripts executable
chmod +x install.sh
chmod +x scripts/*.sh

Run installer (builds llama.cpp and offers per-model downloads)
./install.sh

Answer Y/n for each model download prompt.

Models are stored at /storage/emulated/0/AI_Models/.ultra_ai/models/

Start Ultra AI
./scripts/start_all.sh

UI: http://127.0.0.1:8080

API: http://127.0.0.1:8765

Stop Ultra AI
./scripts/stop_all.sh

Model Configuration
The file models.json defines all models and ports:

Gatekeeper: Meta-Llama-3-8B-Instruct (port 8082)

Librarian: Qwen2-1.5B-Instruct (port 8083)

Specialists: Qwen2-7B, Mistral-7B, Zephyr-7B, Phi-3-mini, DeepSeek-Coder-Lite, stable-code-3b, CodeLlama-7B (ports 8084–8090)

Quantization: Q4_K_M for speed/memory balance on mobile

File/Folder Layout

models.json # model list + ports + paths

install.sh # one-time installer (Termux)

backend/

main.py # orchestrator (API on :8765)

resource_controller.py # RAM/CPU checks + start/stop logic

gatekeeper.py # calls GK model server

librarian.py # calls Librarian + basic KB stubs

specialist.py # chooses/calls Specialists

scripts/

start_all.sh # start GK, Librarian, backend, UI

stop_all.sh # stop everything

start_model.sh # start a specific model by name/role

stop_model.sh # stop a specific model by name/role

frontend/

index.html # web UI

app.js # UI logic + API calls + offline fallback

data/ # created automatically for KB storage

How It Works (High Level)

You ask a question in the web UI.

Backend asks Gatekeeper first. If confident → returns.

If not, Librarian provides a concise assist; Gatekeeper refines.

If still not enough, UI asks “Dive deeper?”.

On confirmation, a Specialist is started (pausing others if needed), answers, then the system cleans up.

Common Commands

Start only the Gatekeeper:
./scripts/start_model.sh gatekeeper

Stop only the Librarian:
./scripts/stop_model.sh librarian

Start everything:
./scripts/start_all.sh

Stop everything:
./scripts/stop_all.sh

Notes

First run builds llama.cpp (takes a few minutes).

You can skip large models during install and add them later by re-running install.sh.

If storage is tight, prefer smaller models like Phi-3-mini-4k and stable-code-3b.

License
MIT

Credits

llama.cpp by Georgi Gerganov and contributors

Model quantizations from bartowski and TheBloke on Hugging Face
