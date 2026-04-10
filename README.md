# NVMe Drive Failure Prediction System 🤖

**Predict drive failures before they happen.** Real-time ML-powered maintenance insights.

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.11+, Node.js 18+

### Setup

```bash
# Clone
git clone https://github.com/Shreeja-88/drive-failure-prediction-system.git
cd drive-failure-prediction-system

# Generate ML model (one-time)
cd ml-model && python train.py && cd ..

# Backend - Terminal 1
cd backend && pip install -r requirements.txt && python app.py

# Frontend - Terminal 2
cd frontend && npm install && npm start
```

### Sample Dataset
- A small sample dataset covering all failure modes is available at `data/sample_failure_modes.csv`

**Access Dashboard:** http://localhost:3000

### Quick Docker Deploy

```bash
docker-compose up -d
curl http://localhost:5000/api/health
```

---

## Features

**Smart Analytics**
- Failure mode distribution analysis
- Top 5 failure patterns detected
- Fleet health metrics
- Per-drive risk scoring

**ML-Powered Predictions**
- 5 failure categories: wear-out, thermal, power-related, firmware, early-life
- RandomForest classifier (97%+ accuracy)
- Real-time drive health prediction
- Handles imbalanced data (98% healthy, 2% failing)

**Professional UI**
- Purple gradient startup-style theme
- Responsive design (mobile-friendly)
- Real-time chart updates
- Intuitive record selection

**Production-Ready**
- Docker containerization
- Multi-stage builds
- Health checks & monitoring
- CORS security

---

## API

```bash
GET /api/health
POST /api/predict  (JSON body with drive attributes)
```

---

## Deployment

Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)

Options:
- **Heroku:** `git push heroku main`
- **AWS/DigitalOcean:** See DEPLOYMENT.md
- **Docker:** `docker build -t nvme-dashboard:latest .`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -ti:5000 \| xargs kill -9` |
| Model missing | `cd ml-model && python train.py` |
| CORS error | Update `CORS_ORIGINS` in `.env` |
| API offline | Verify backend: `curl http://localhost:5000/api/health` |

---

## License

MIT License - See LICENSE for details

---

**Predictive maintenance for modern NVMe storage** 
