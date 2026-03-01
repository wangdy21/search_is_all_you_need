#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== Search Is All You Need ==="

# 1. Check/create Python venv
if [ ! -d "venv" ]; then
    echo "[1/4] Creating Python virtual environment..."
    python -m venv venv
fi

echo "[1/4] Activating virtual environment..."
source venv/bin/activate

# 2. Install Python dependencies
echo "[2/4] Installing Python dependencies..."
pip install -q -r backend/requirements.txt

# 3. Build frontend (if node available)
export PATH="/usr/local/bin:$PATH"
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VER" -ge 18 ]; then
        echo "[3/4] Building frontend..."
        cd frontend
        npm install --silent
        npx vite build
        cd ..
    else
        echo "[3/4] SKIP: Node.js >= 18 required (found v$NODE_VER)"
    fi
else
    echo "[3/4] SKIP: Node.js not found"
fi

# 4. Create .env if missing
if [ ! -f ".env" ]; then
    echo "[INFO] Creating .env from .env.example..."
    cp .env.example .env
    echo "[INFO] Please edit .env to set your ZHIPU_API_KEY"
fi

# 5. Start Flask server
echo "[4/4] Starting Flask server on port 5000..."
echo "       Access: http://localhost:5000"
python backend/app.py
