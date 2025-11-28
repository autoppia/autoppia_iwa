# Demo Webs Setup Guide

IWA requires demo web applications to run benchmarks. These webs can run **locally** or be accessed **remotely**.

## 🌍 **Deployment Modes**

IWA supports two modes:

| Mode | Use Case | Setup |
|------|----------|-------|
| **Local** | Development, testing | Run webs on your machine |
| **Remote** | Production, CI/CD | Connect to deployed webs |

---

## 🏠 **Option 1: Local Development**

### **Prerequisites:**
- Docker and Docker Compose installed
- Ports 8090-8113 available

### **Steps:**

#### **1. Clone Demo Webs Repository**
```bash
cd ..
git clone https://github.com/autoppia/autoppia_webs_demo
cd autoppia_webs_demo
```

#### **2. Start Demo Webs**
```bash
# Start all webs with setup script
./scripts/setup.sh

# Or start individually:
docker-compose up web_1_demo_movies  # Port 8100
docker-compose up web_2_demo_books   # Port 8101
docker-compose up webs_server        # Port 8090
```

#### **3. Configure IWA**
```bash
cd ../autoppia_iwa

# Add to .env:
echo "DEPLOYMENT_MODE=local" >> .env
echo "DEMO_WEBS_ENDPOINT=http://localhost" >> .env
```

#### **4. Verify**
```bash
# Check webs are running:
curl http://localhost:8090/health  # webs_server
curl http://localhost:8100/        # web_1
curl http://localhost:8101/        # web_2
```

---

## 🌐 **Option 2: Remote (Production)**

### **Use deployed webs on a server:**

#### **1. Configure IWA**
```bash
# Add to .env:
echo "DEPLOYMENT_MODE=remote" >> .env
echo "DEMO_WEBS_ENDPOINT=http://your-production-server.com" >> .env
```

#### **2. Verify**
```bash
# Check webs are accessible:
curl http://your-production-server.com:8090/health
curl http://your-production-server.com:8100/
```

---

## 📋 **Port Mapping**

| Service | Port | URL |
|---------|------|-----|
| webs_server (backend) | 8090 | http://localhost:8090 |
| web_1_demo_movies | 8100 | http://localhost:8100 |
| web_2_demo_books | 8101 | http://localhost:8101 |
| web_3_autozone | 8102 | http://localhost:8102 |
| web_4_autodining | 8103 | http://localhost:8103 |
| web_5_autocrm | 8104 | http://localhost:8104 |
| web_6_automail | 8105 | http://localhost:8105 |
| web_7_autodelivery | 8106 | http://localhost:8106 |
| web_8_autolodge | 8107 | http://localhost:8107 |
| web_9_autoconnect | 8108 | http://localhost:8108 |
| web_10_autowork | 8109 | http://localhost:8109 |
| web_11_autocalendar | 8110 | http://localhost:8110 |
| web_12_autolist | 8111 | http://localhost:8111 |
| web_13_autodrive | 8112 | http://localhost:8112 |

---

## 🔧 **Environment Variables**

```bash
# Required:
DEPLOYMENT_MODE=local|remote
DEMO_WEBS_ENDPOINT=http://localhost  # or remote URL

# Optional (defaults shown):
DEMO_WEBS_STARTING_PORT=8100
DEMO_WEB_SERVICE_PORT=8090
```

---

## ✅ **Testing Connection**

```bash
# Quick test
python3 -c "
import requests
print('Testing webs connection...')
resp = requests.get('http://localhost:8090/health', timeout=5)
print(f'✅ webs_server: {resp.status_code}')
resp = requests.get('http://localhost:8100/', timeout=5)
print(f'✅ web_1: {resp.status_code}')
print('All good!')
"
```

---

## 🐛 **Troubleshooting**

### **Webs not starting?**
```bash
# Check Docker
docker ps

# Restart webs
cd autoppia_webs_demo
docker-compose down
docker-compose up -d
```

### **Port conflicts?**
```bash
# Check what's using ports
lsof -i :8090
lsof -i :8100

# Kill process or change DEMO_WEBS_STARTING_PORT
```

### **Connection refused?**
```bash
# Check firewall
sudo ufw status

# Or check .env configuration
cat .env | grep DEMO_WEBS
```

---

## 📝 **Why Separate Repository?**

**autoppia_iwa** (this repo):
- Pure evaluation system
- No web deployment code
- Agent-agnostic

**autoppia_webs_demo** (separate repo):
- Web applications code
- Deployment scripts
- Independent updates

**Benefits:**
- ✅ Clean separation of concerns
- ✅ IWA stays lightweight
- ✅ Webs can be deployed anywhere
- ✅ No Git submodule conflicts
- ✅ Easier maintenance
