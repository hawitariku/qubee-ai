@echo off
echo ========================================
echo   Qubee AI Installation Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [4/4] Verifying installation...
python -c "import fastapi, uvicorn; print('✓ FastAPI installed')"
python -c "import transformers; print('✓ Transformers installed')"
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start Qubee AI, run:
echo   python main.py
echo.
echo Then open your browser to:
echo   http://localhost:8082
echo.
pause
