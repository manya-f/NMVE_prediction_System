# 🗂️ File Navigation Guide

This project has **MULTIPLE VERSIONS** of some files. This guide explains which ones to use.

---

## 📋 Quick Answer

### For the Complete Web App (Recommended)
Use these files:
- ✅ **app_complete.py** ← Main Flask server
- ✅ **templates/index_complete.html** ← Web UI  
- ✅ **static/style_complete.css** ← CSS styling
- ✅ **static/script_complete.js** ← JavaScript logic

### Start the app:
```bash
python app_complete.py
```

Then open: **http://localhost:5000**

---

## 📁 Complete File Listing

### Root Level Files
```
app.py .......................... Simple standalone Flask app (alternate)
app_complete.py ................ MAIN Flask app ⭐ USE THIS
train.py ....................... Simple standalone training (alternate)
preprocess.py .................. Data preprocessing (alternate)
requirements.txt ............... Python dependencies
SETUP_GUIDE.md ................. Detailed setup instructions
COMPLETE_SYSTEM_GUIDE.md ....... This complete overview ⭐
FILE_NAVIGATION.md ............. This file (you are here)
```

### Templates (Folder)
```
templates/
├── index.html ................. Simple HTML version (alternate)
├── index_complete.html ........ MODERN UI ⭐ USE THIS
└── [historical versions]
```

### Static Files (Folder)
```
static/
├── style.css .................. Simple CSS (alternate)
├── style_complete.css ......... PROFESSIONAL CSS ⭐ USE THIS
├── script.js .................. Basic JavaScript (alternate)
└── script_complete.js ......... ADVANCED JAVASCRIPT ⭐ USE THIS
```

### ML Model (Folder)
```
ml-model/
├── nvme_failure_mode_model.pkl .... MAIN MODEL ✅ (trained)
├── feature_columns.pkl ........... Feature schema ✅ (trained)
├── train_failure_modes.py ........ Multiclass trainer
├── train.py ...................... Binary classifier trainer
├── predict.py .................... Binary prediction module
├── single_drive_predictor.py ..... Single-drive wrapper
├── [other analysis files]
└── __pycache__/
```

### Backend (Folder) - Legacy React Version
```
backend/
├── app.py ...................... React dashboard backend (alternate)
└── requirements.txt ............ Separate dependencies
```

### Frontend (Folder) - Legacy React Version
```
frontend/
├── src/ ........................ React components
├── package.json ............... Node.js dependencies
└── [React config files]
```

### Data (Folder)
```
data/
├── NVMe_Drive_Failure_Dataset.csv .. Main dataset (5,000 rows)
└── sample_failure_modes.csv ........ Quick test samples ⭐
```

---

## 🎯 Which Version to Use?

### Option 1: Complete Web App ⭐ (Recommended)
**For:** Modern web interface with interactive prediction

**Start with:**
```bash
python app_complete.py
```

**Files involved:**
- app_complete.py
- templates/index_complete.html
- static/style_complete.css
- static/script_complete.js

**Features:**
- Clean, modern UI
- Real-time predictions
- All 6 failure modes displayed
- Progress bars & animations
- Mobile-responsive

---

### Option 2: React Dashboard (Legacy)
**For:** Advanced React-based dashboard with multiple pages

**Start with:**
```bash
cd backend && python app.py    # Terminal 1
cd frontend && npm start       # Terminal 2
```

**Files involved:**
- backend/app.py
- frontend/src/App.js
- frontend/package.json

**Features:**
- CSV batch uploads
- Multiple dashboard pages
- Real-time charts
- Complex React architecture

---

### Option 3: Simple Standalone Flask
**For:** Minimal setup, quick testing

**Start with:**
```bash
python app.py
```

**Files involved:**
- app.py
- templates/index.html
- static/style.css

**Features:**
- Minimal dependencies
- Basic prediction interface
- No animations

---

## 🚀 Getting Started (Fastest Path)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Complete App
```bash
python app_complete.py
```

### 3. Open Web Browser
```
http://localhost:5000
```

### 4. Test with Sample
Click any "Quick Sample" button to auto-fill the form

---

## 📊 Architecture Comparison

| Aspect | Complete App | React Dashboard | Simple Flask |
|--------|--------------|-----------------|--------------|
| **UI Framework** | HTML/CSS/JS | React | HTML/Vanilla JS |
| **Pages** | Single | Multiple | Single |
| **Input Type** | Single drive | CSV or single | Single drive |
| **Charts** | Progress bars | Recharts | None |
| **Animations** | Smooth | Full page | Basic |
| **Setup Time** | 2 minutes | 5 minutes | 1 minute |
| **Recommended** | ✅ YES | For complex dashboards | For testing |

---

## 🔄 Version History

### Complete App (NEW)
- app_complete.py
- templates/index_complete.html
- static/style_complete.css
- static/script_complete.js

**When:** Latest build  
**Status:** ✅ Production-ready

### Simple Flask (ORIGINAL)
- app.py
- preprocess.py
- train.py
- templates/index.html

**When:** Initial implementation  
**Status:** ✅ Working but basic

### React Dashboard (ADVANCED)
- backend/app.py (Flask backend)
- frontend/ (React components)

**When:** Extended development  
**Status:** ✅ Feature-rich but complex

---

## 🎨 UI Comparison

### Complete App (index_complete.html)
```
[Modern Dark Theme]
┌─────────────────────────────────────┐
│  NVMe Drive Health Predictor        │
│  Real-time ML-powered detection     │
├─────────────────────────────────────┤
│ INPUT FORM   │   RESULTS            │
│              │   ✓ Health Status    │
│ Temp: [____] │   📊 All 6 Modes    │
│ Hours: [___] │   ⚡ Progress Bars   │
│ Life: [___]  │   📈 Confidence     │
│              │                     │
│ [Analyze]    │                     │
└─────────────────────────────────────┘
```

### Simple Flask (index.html)
```
[Minimal Design]
┌──────────────────────────┐
│ NVMe Failure Predictor   │
├──────────────────────────┤
│ INPUT FORM │ RESULTS     │
│            │             │
│ Temp: [__] │ Status: ... │
│ Hours: [_] │ Risk: ...   │
│ Life: [__] │ Mode: ...   │
│            │             │
│  [Predict] │             │
└──────────────────────────┘
```

---

## 💡 Decision Tree

```
START HERE
│
├─ "I want a modern web app"
│  └─→ Use: app_complete.py ⭐
│
├─ "I need multiple pages & charts"
│  └─→ Use: backend/app.py + frontend/
│
├─ "I just want to test the model"
│  └─→ Use: ml-model/predict.py (no Flask)
│
└─ "I need minimal setup"
   └─→ Use: app.py (simple)
```

---

## 🧪 Testing Each Version

### Test Complete App
```bash
python app_complete.py
# Open http://localhost:5000
# Click "Quick Samples" buttons
```

### Test Simple Flask
```bash
python app.py
# Open http://localhost:5000
# Fill form manually
```

### Test Direct ML Model
```python
from ml_model.predict import predict_drive

result = predict_drive({
    "Vendor": "Samsung",
    "Model": "980 Pro",
    "Firmware_Version": "1.0",
    "Temperature_C": 45.5,
    "Power_On_Hours": 15000,
    "Percent_Life_Used": 62,
    "Unsafe_Shutdowns": 2,
    "Media_Errors": 1,
    "Total_TBW_TB": 100,
    "Total_TBR_TB": 95,
    "Available_Spare": 95,
})
print(result)
```

---

## 🚀 Deployment Options

### Deploy Complete App
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 app_complete:app

# Using Heroku
git push heroku main

# Using Docker
docker build -t nvme-app .
docker run -p 5000:5000 nvme-app
```

### Deploy React Dashboard
```bash
# Check DEPLOYMENT.md for full instructions
# Requires both backend and frontend builds
```

---

## 📞 Support

### Issue: "Port already in use"
**Solution:**
```bash
# Find process on port 5000
netstat -ano | findstr :5000

# Kill it
taskkill /PID [number] /F
```

### Issue: "Template not found"
**Solution:**
- Ensure templates/ folder exists in project root
- Check spelling: `index_complete.html` (not `index.html`)

### Issue: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Model not found"
**Solution:**
Check that:
```bash
ls ml-model/nvme_failure_mode_model.pkl
ls ml-model/feature_columns.pkl
```

---

## ✅ Checklist for Complete App

- [ ] Python 3.11+ installed
- [ ] requirements.txt dependencies installed
- [ ] ML model files exist in ml-model/
- [ ] Flask server starts without errors
- [ ] Can access http://localhost:5000
- [ ] Form loads with buttons
- [ ] Sample button works
- [ ] API returns predictions
- [ ] Results display correctly

---

## 📝 Quick Reference

### Start Complete App
```bash
python app_complete.py
```

### Start Simple Flask
```bash
python app.py
```

### Start React Dashboard
```bash
cd backend && python app.py &
cd frontend && npm start
```

### Train ML Model
```bash
cd ml-model
python train_failure_modes.py
```

### Test API Directly
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature": 45.5, "power_on_hours": 15000, "life_used": 62, "unsafe_shutdowns": 2, "media_errors": 1}'
```

---

**TL;DR:** Start with `python app_complete.py` and open http://localhost:5000
