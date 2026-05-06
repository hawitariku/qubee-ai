#!/bin/bash

echo "========================================"
echo "  Qubee AI Installation Script"
echo "========================================"
echo ""

# Check Python installation
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi
python3 --version
echo ""

# Upgrade pip
echo "[2/4] Upgrading pip..."
python3 -m pip install --upgrade pip
echo ""

# Install dependencies
echo "[3/4] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

# Verify installation
echo "[4/4] Verifying installation..."
python3 -c "import fastapi, uvicorn; print('✓ FastAPI installed')"
python3 -c "import transformers; print('✓ Transformers installed')"
echo ""

echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "To start Qubee AI, run:"
echo "  python3 main.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:8082"
echo ""
