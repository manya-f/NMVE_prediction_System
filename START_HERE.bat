@echo off
REM NVMe Drive Failure Predictor - Complete Startup Script
REM Run this file to start everything automatically!

cls
echo.
echo ========================================
echo   NVMe DRIVE FAILURE PREDICTOR
echo   Complete Startup Script
echo ========================================
echo.

REM Check if model exists
if not exist "models\model.pkl" (
    echo [!] Model not found! Training model...
    cd ml-model
    python train_simple.py
    cd ..
    echo [✓] Model training complete!
    echo.
)

REM Start Flask Backend
echo [*] Starting Flask Backend on port 5000...
echo [*] Open a new terminal if needed...
echo.
python app.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Flask failed to start!
    echo Check the error messages above
    pause
)
