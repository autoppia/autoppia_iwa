# 🚀 Project Setup Guide

This guide walks you through setting up and running the project locally on a Linux machine, including Python installation, virtual environment setup, Playwright configuration, and project dependencies.

---

## 📋 1. Introduction

To ensure proper project functioning, **three essential components** must run simultaneously:

### **Core Components**

| Component | Purpose | Setup Reference |
|-----------|---------|-----------------|
| 🤖 **`LLM`** | Local Or External model server | [Model Deployment Guide](../../modules/llm_local/setup.md) |
| 🌐 **Demo webapps** | Demo application for testing | Check its own **setup.md** |
| 🕷️ **Web Agent** | Browser automation agent | Configured via AGENT_PORT |

> ⚠️ **Important**: Review the following steps and required ports before starting all components.

---

### **1.2 LLM REQUIRED**

### 🤖 LLM Configuration

You have **multiple options** for LLM integration:

#### **Option A: External LLM APIs** 🌐 (Recommended - CPU Only)
Use any external LLM service:
- **OpenAI** (GPT-4, GPT-3.5)
- **DeepSeek**
- **Anthropic Claude**
- **Any other API provider**

**Benefits:**
- ✅ No GPU required
- ✅ No local setup needed
- ✅ Always up-to-date models
- ✅ Lower maintenance

#### **Option B: Local LLM Models** 🖥️ (GPU Required)

| Model Name | Variant | GPU Memory | Open Source | Model Link |
|------------|---------|------------|-------------|------------|
| **Qwen 2.5 Coder 32B** | Q2_K | 18 GB | ✅ Yes | [Qwen2.5-Coder-32B](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF) |
| **Qwen 2.5 Coder 14B** | Q4_K_M | 18 GB | ✅ Yes | [Qwen2.5-Coder-14B](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF) |
| **Hermes LLAMA 3.1** | Q4_K_M | 12 GB | ✅ Yes | [LLAMA Model](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF) |

---
💡 **Note**: Ensure your hardware or cloud setup meets these GPU memory requirements for inference.

---

## 🔧 2. Project Setup

### **Prerequisites**

- 🐍 **Python 3.10 or above**
- 📦 **pip** (Python package manager)
- 🐍 **Conda** (Optional for environment management)
- 🔐 **sudo/root privileges** for system dependencies
- 🗄️ **Django App Database**: Follow database setup in the app's `setup.md`

---

## 📥 INSTALLATION

### **Step 1: Verify Python Installation**

```bash
python3 --version
```

**If version is earlier than 3.10** (Ubuntu):
```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip
```

---

### **Step 2: Environment Setup**

#### **Virtual Environment with `venv`**

**Create virtual environment:**
```bash
python3 -m venv venv
```

> 💡 **Note**: If Python version issues occur, specify explicitly:
```bash
python3.10 -m venv venv
```

**Activate environment:**
```bash
source venv/bin/activate
```

---

### **Step 3: Install Dependencies**

**Python dependencies:**
```bash
pip install -r requirements.txt
```

**Playwright and browser binaries:**
```bash
python3 -m playwright install
```
*This installs Chromium, Firefox, and WebKit.*

---

### **Step 4: Environment Configuration**

#### **Create `.env` file** (if you don't have one):
```bash
touch .env
```

#### **Add required environment variables:**
```env
# LLM Provider Configuration
# Can be "serverless", "local", or "openai"
LLM_PROVIDER="local"

# Local LLM Configuration
LOCAL_MODEL_ENDPOINT="http://192.168.0.103:6000/generate"

# OpenAI Configuration
OPENAI_API_KEY=""  # We suggest using an API key for simplicity
OPENAI_MODEL="gpt-4o-mini"
OPENAI_MAX_TOKENS="2000"
OPENAI_TEMPERATURE="0.7"

# Demo Webs Endpoint Configuration
DEMO_WEBS_ENDPOINT="http://localhost"
DEMO_WEBS_STARTING_PORT=8000

# Agent Configuration
AGENT_NAME="autoppia_agent"
AGENT_HOST="localhost"
AGENT_PORT="9000"  # Port where the web agent will be deployed
EVALUATOR_HEADLESS="False"
```

#### **Configuration Options**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEMO_WEBS_ENDPOINT` | Base URL for demo webs | `http://localhost` | `http://192.168.1.100` |
| `DEMO_WEBS_STARTING_PORT` | Starting port for demo webs | `8000` | `9000` |
| `AGENT_HOST` | Hostname where agent runs | `localhost` | `84.247.180.39` |
| `AGENT_PORT` | **Port where web agent is deployed** | `9000` | `8080` |
| `EVALUATOR_HEADLESS` | Run browser in headless mode | `False` | `True` |

💡 **Important**: `AGENT_PORT` specifies where your web agent will be deployed and accessible.

**Verify configuration:**
```bash
cat .env
```

---

### **Step 5: Demo Webs Setup** 🌐

#### **Prerequisites**
- 🐳 Docker and Docker Compose installed

#### **Installation**
```bash
CURRENT_DIR=$(pwd)
cd autoppia_iwa_module/modules/webs_demo/scripts

# Install Docker
chmod +x install_docker.sh
./install_docker.sh

# Setup demo webs
chmod +x setup.sh
./setup.sh

cd "$CURRENT_DIR"
```

#### **Configuration** (Optional)
Edit `.env` to customize endpoints:
```bash
DEMO_WEBS_ENDPOINT=http://localhost
DEMO_WEBS_STARTING_PORT=8000
```

🔧 **Remote Setup**: Change endpoint to your demo webs server IP for distributed deployment.

---

### **Step 6: Test Browser User Profile** 🧪

This script tests browser automation with persistent user profiles:

**What it does:**
1. **🚀 Setup & Launch**: Loads user profile directory and launches Chromium
2. **🔐 Authentication Check**: Handles login/registration if no session exists
3. **⚙️ Event Processing**: Retrieves and processes events, saves to database
4. **🧹 Clean Up**: Properly closes browser after operations

---

## 📝 Important Notes

### **Environment Activation**
Always activate your environment before development:
```bash
source venv/bin/activate
```

### **Playwright Browsers**
Reinstall browsers if needed:
```bash
python3 -m playwright install
# or
playwright install
```

### **Dependencies Management**
Update requirements after adding new packages:
```bash
pip freeze > requirements.txt
```

### **Port Management**
Ensure the following ports are available:
- 🤖 **LLM Server**: 6000 (default)
- 🌐 **Demo Webs**: 8000+ (configurable)
- 🕷️ **Web Agent**: 9000 (configurable via AGENT_PORT)

---

## ✅ Ready to Go!

Your project should now be ready to run. If you encounter any issues:
- 📖 Review the setup steps
- 📚 Consult project documentation
- 🔍 Check port availability and conflicts

🎉 **Success**: All components configured and ready for development!

---

## 🆘 Support & Contact

Need help? Contact our team on Discord:
- **@Daryxx**
- **@Riiveer**
