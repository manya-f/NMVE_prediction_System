# 🚀 Complete Setup Guide - NVMe Drive Failure Predictor

## ⚡ Quick Start (Choose One)

### Option A: Automatic Startup (EASIEST)
```
Double-click: START_HERE.bat
```
This runs everything automatically!

---

### Option B: Manual Startup (2 Terminals)

**Terminal 1 - Backend (Flask)**
```powershell
python app.py
```
You should see:
```
============================================================
  🚀 NVMe Drive Failure Predictor API
============================================================
📍 Starting on http://0.0.0.0:5000
🔗 Frontend will connect to http://localhost:5000

API Endpoints:
  GET  /api/health       - Check if API is running
  POST /api/predict      - Predict drive failure
============================================================
```

**Terminal 2 - Frontend (React)**
```powershell
cd frontend
npm start
```
Browser opens to: `http://localhost:3000`

---

## ✅ Verification Checklist

1. **Backend Running?**
   ```powershell
   curl http://localhost:5000/api/health
   ```
   Expected: `{"status":"healthy","message":"API is running"}`

2. **Frontend Running?**
   - Open **http://localhost:3000**
   - Top right should show **"API Connected" ✓**

3. **Model Loaded?**
   - Check you see `✓ Model loaded successfully` in Flask terminal

4. **Ready to Test?**
   - Go to **Single Drive** or **Predictions** page
   - Enter SMART metrics
   - Click **Predict Drive Status**

---

## 🔧 If Something Fails

### Problem: "Model not found"
**Solution:**
```powershell
cd ml-model
python train_simple.py
cd ..
python app.py
```

### Problem: "Port 5000 already in use"
**Solution:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
python app.py
```

### Problem: "CORS errors in browser"
**Solution:** Kill all Python processes and restart
```powershell
taskkill /IM python.exe /F
python app.py
```

### Problem: "Failed to fetch API"
**Solution:** 
1. Check Flask terminal - are there errors?
2. Hard refresh browser: `Ctrl+Shift+R`
3. Verify "API Connected" shows in top right

---

## 📊 API Usage

### Single Drive Prediction
**POST** `http://localhost:5000/api/predict`

```json
{
  "temperature": 40,
  "power_on_hours": 5000,
  "life_used": 20,
  "unsafe_shutdowns": 1,
  "media_errors": 0
}
```

**Response:**
```json
{
  "success": true,
  "prediction": "Healthy ✓",
  "failure_risk": "15.3%",
  "possible_failure_mode": "✓ Healthy",
  "metrics": {
    "temperature_c": 40,
    "power_on_hours": 5000,
    "life_used_percent": 20,
    "unsafe_shutdowns": 1,
    "media_errors": 0
  }
}
```

---

## 🎯 Features Implemented

✅ **ML Model** - Predicts 6 failure modes  
✅ **Backend API** - Flask with CORS enabled  
✅ **Frontend** - React dashboard with multiple pages  
✅ **Single Drive Predictor** - Input form with real-time predictions  
✅ **Batch Predictions** - Upload CSV and analyze drives  
✅ **Insights Page** - Risk analysis and patterns  
✅ **Health Check** - API status monitoring  

---

## 📱 Pages Available

1. **Dashboard** - Overview of drives
2. **Drives** - List all drives from CSV
3. **Predictions** - Batch predictions
4. **Single Drive** ⭐ - Input form for single drive
5. **Insights** - Risk analysis

---

## 🆘 Support

If problems persist:

1. **Check Flask output** for error messages
2. **Check browser console** (F12 → Console)
3. **Verify model exists:** `ls models/model.pkl`
4. **Ensure both ports free:** 3000 and 5000

---

**Ready?** Start with `START_HERE.bat` or follow **Option B** above!
