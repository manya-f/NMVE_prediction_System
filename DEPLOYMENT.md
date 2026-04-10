# 🚀 Deployment Guide: NVMe Drive Failure Dashboard

## Overview
This guide covers deploying the NVMe Drive Failure Dashboard for production use.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Quick Start

```bash
# Clone repository
git clone https://github.com/Shreeja-88/drive-failure-prediction-system.git
cd drive-failure-prediction-system

# Generate ML artifacts (one time)
cd ml-model
python train.py
cd ..

# Backend setup
cd backend
pip install -r requirements.txt
python app.py
# Backend running on http://localhost:5000

# Frontend setup (new terminal)
cd frontend
npm install
npm start
# Frontend running on http://localhost:3000
```

Access dashboard: **http://localhost:3000**

---

## 2. Docker Deployment (Recommended)

### Prerequisites
- Docker & Docker Compose installed

### Build & Run

```bash
# Build Docker image
docker build -t nvme-dashboard:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f nvme-dashboard

# Stop services
docker-compose down
```

Access dashboard: **http://localhost:5000**

### Verify Deployment
```bash
curl http://localhost:5000/api/health
# Expected response: {"status": "ok"}
```

---

## 3. Cloud Deployment

### Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### AWS (EC2)

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker

# Clone and deploy
git clone https://github.com/Shreeja-88/drive-failure-prediction-system.git
cd drive-failure-prediction-system
docker-compose up -d
```

### DigitalOcean App Platform

1. Connect your GitHub repository
2. Set runtime to Docker
3. Configure environment variables (see `.env.example`)
4. Deploy

---

## 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Update variables for your deployment:
- `FLASK_ENV`: Set to `production`
- `SECRET_KEY`: Use strong random key
- `CORS_ORIGINS`: Set to your domain
- `LOG_LEVEL`: Set to `INFO` or `WARNING`

---

## 5. Performance & Monitoring

### Enable HTTPS
Use nginx as reverse proxy with SSL certificates (Let's Encrypt):

```nginx
upstream backend {
    server localhost:5000;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Health Checks
- Backend: `GET /api/health`
- Monitor logs: `docker-compose logs -f`

---

## 6. Troubleshooting

### Model artifacts not found
```bash
cd ml-model
python train.py
```

### Port already in use
```bash
# On Mac/Linux
lsof -ti:5000 | xargs kill -9

# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### CORS errors
Update `CORS_ORIGINS` in `.env` to match frontend URL

---

## 7. Production Checklist

- [ ] ML model artifacts generated
- [ ] `.env` file configured with production values
- [ ] HTTPS/SSL enabled
- [ ] Health checks passing
- [ ] Backups configured
- [ ] Monitoring/alerting set up
- [ ] Rate limiting configured
- [ ] CORS properly restricted

---

## Support
For issues, open a GitHub issue or contact the maintainers.
