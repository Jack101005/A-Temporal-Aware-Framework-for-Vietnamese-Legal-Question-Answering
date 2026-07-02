#!/usr/bin/env bash
# start_all.sh — bring up the full stack for the VN Legal Temporal-RAG app
# Opens 3 new Terminal windows (Ollama, FastAPI, Frontend). PostgreSQL
# must already be started via the Postgres.app menu-bar icon.

PROJECT_DIR="$HOME/Desktop/vn-legal-rag"
SSD_MODELS="/Volumes/Jack/ollama-models"

# ---- 0) sanity checks ---------------------------------------------------
if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ Project not found at $PROJECT_DIR"; exit 1
fi
if [ ! -d "$SSD_MODELS" ]; then
  echo "❌ SSD not mounted at /Volumes/Jack. Plug it in and try again."; exit 1
fi
if ! pg_isready -q -h localhost 2>/dev/null; then
  echo "⚠️  PostgreSQL not responding on localhost."
  echo "   → Open Postgres.app and click Start, then re-run this script."
  exit 1
fi
echo "✓ Project dir OK"
echo "✓ SSD mounted"
echo "✓ PostgreSQL is up"
echo ""

# ---- helper: open a new Terminal window running a command --------------
# Writes the command to a temp .command file (which Terminal executes),
# so we don't fight AppleScript escaping.
open_tab() {
  local title="$1"
  local cmd="$2"
  local tmp
  tmp="$(mktemp -t vnlegal-XXXX).command"
  cat > "$tmp" <<EOF
#!/bin/bash
echo -ne "\033]0;${title}\007"
${cmd}
EOF
  chmod +x "$tmp"
  open -a Terminal "$tmp"
  sleep 1
}

# ---- 1) Ollama server ---------------------------------------------------
echo "→ Starting Ollama (SSD models)..."
open_tab "Ollama" "export OLLAMA_MODELS=\"$SSD_MODELS\"; ollama serve"

echo -n "  waiting for Ollama"
for i in {1..30}; do
  if curl -s http://localhost:11434 >/dev/null 2>&1; then
    echo " ✓"; break
  fi
  echo -n "."
  sleep 1
done

# ---- 2) FastAPI ---------------------------------------------------------
echo "→ Starting FastAPI (port 8000)..."
open_tab "FastAPI" "cd \"$PROJECT_DIR\" && source .venv/bin/activate && export DATABASE_URL=\"postgresql://jacktrinh@localhost/vn_legal\" && python -m uvicorn src.api.main:app --reload --port 8000"

echo -n "  waiting for FastAPI"
for i in {1..90}; do
  if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo " ✓"; break
  fi
  echo -n "."
  sleep 1
done

# ---- 3) Frontend --------------------------------------------------------
echo "→ Starting frontend (port 3000)..."
open_tab "Frontend" "cd \"$PROJECT_DIR/src/frontend\" && npx serve -l 3000"

sleep 3

# ---- 4) open the browser ------------------------------------------------
echo "→ Opening http://localhost:3000 ..."
open "http://localhost:3000"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  All services started. To stop, close each Terminal window."
echo "═══════════════════════════════════════════════════════════════"
