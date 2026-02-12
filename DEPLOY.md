# 🚀 PrismOps Deployment Log (v1.0)

## 1. Server Configuration
- **Cloud Provider:** AWS EC2 (Seoul Region / ap-northeast-2)
- **Instance Type:** t2.medium
- **OS:** Ubuntu Server 22.04 LTS
- **Public IP:** 3.38.218.230

## 2. Infrastructure Stack
- **Container Runtime:** Docker & Docker Compose
- **Service Ports:**
  - `8501`: Streamlit Chat UI (Frontend)
  - `8000`: FastAPI Server (Backend)
  - `3000`: Grafana Dashboard (Monitoring)
  - `9090`: Prometheus (Metrics)

## 3. Deployment Command History
```bash
# Initial Setup
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git

# Repository Clone & Setup
git clone [https://github.com/SonHyeokjin/PrismOps.git](https://github.com/SonHyeokjin/PrismOps.git)
cd PrismOps
# (.env file created manually)

# Service Launch
sudo docker-compose up -d --build