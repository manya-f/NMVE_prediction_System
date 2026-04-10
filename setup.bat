@echo off
REM Quick Setup Script for Windows

echo NVMe Drive Failure Dashboard - Windows Setup
echo ==========================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 not found. Install Python 3.11+
    exit /b 1
)
echo ✓ Python found

REM Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js not found. Install Node.js 18+
    exit /b 1
)
echo ✓ Node found

echo.
echo Setting up ML model...
cd ml-model
if not exist "nvme_rf_model.pkl" (
    echo Training model... ^(this takes ~30 seconds^)
    python train.py
    echo ✓ Model trained
) else (
    echo ✓ Model already exists
)
cd ..

echo.
echo 🔧 Setting up backend...
cd backend
pip install -r requirements.txt >nul 2>&1
echo ✓ Backend dependencies installed
cd ..

echo.
echo ⚛️  Setting up frontend...
cd frontend
call npm install >nul 2>&1
echo ✓ Frontend dependencies installed
cd ..

echo.
echo ==========================================
echo ✅ Setup complete!
echo.
echo To run locally:
echo.
echo   Terminal 1 ^(Backend^):
echo     cd backend ^& python app.py
echo.
echo   Terminal 2 ^(Frontend^):
echo     cd frontend ^& npm start
echo.
echo   Access: http://localhost:3000
echo.
echo To run with Docker:
echo     docker-compose up -d
echo.
echo ==========================================
pause
