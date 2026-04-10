#!/bin/bash
# Quick Setup & Deployment Script
# Run this to get started in seconds

set -e

echo "🚀 NVMe Drive Failure Dashboard - Setup Script"
echo "=============================================="

# Check prerequisites
echo "✓ Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.11+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install Node.js 18+"
    exit 1
fi

echo "✓ Python & Node found"

# Generate ML model
echo ""
echo "📊 Setting up ML model..."
cd ml-model
if [ ! -f "nvme_rf_model.pkl" ]; then
    echo "Training RandomForest model... (this takes ~30 seconds)"
    python3 train.py
    echo "✓ Model trained and saved"
else
    echo "✓ Model already exists"
fi
cd ..

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Backend dependencies installed"
cd ..

# Frontend setup
echo ""
echo "⚛️  Setting up frontend..."
cd frontend
npm install > /dev/null 2>&1
echo "✓ Frontend dependencies installed"
cd ..

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo ""
echo "To run locally:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend && python3 app.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend && npm start"
echo ""
echo "  Access: http://localhost:3000"
echo ""
echo "To run with Docker:"
echo "    docker-compose up -d"
echo ""
echo "=============================================="
