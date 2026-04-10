# Multi-stage build for production-ready NVMe dashboard

# Stage 1: Build React frontend
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --frozen-lockfile
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm run build

# Stage 2: Build Python backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY backend/requirements.txt ./backend/
COPY ml-model/ ./ml-model/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Expose ports
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run backend server
WORKDIR /app/backend
CMD ["python", "app.py"]
