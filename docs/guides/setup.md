# **Project Setup Guide**

This guide will walk you through setting up and running the project locally on a Linux machine. It includes steps to install Python 3.10 or above, set up a virtual environment or Conda environment, install Playwright, and configure the project dependencies.

---

## **1. Introduction**

To ensure the proper functioning of the project, three essential components need to be running simultaneously:

1. **`run_local_llm.py`**: Local model server (used if you don't want to use the Runpod serverless model). Check the [Model Deployment Guide](../../modules/llm_local/setup.md) for step-by-step instructions.
2. **Demo (Django) app**: Runs the demo application for testing purposes (check its own **setup.md** for setup instructions).

> **Important:** Review the following steps and required ports before starting all components.

---

### **1.2 Model Information and GPU Requirements**

| Model Name             | Variant | Model Link                                                                             | GPU Memory Requirement | Open Source |
| ---------------------- | ------- | -------------------------------------------------------------------------------------- | ---------------------- | ----------- |
| **Qwen 2.5 Coder 32B** | Q2_K    | [Qwen2.5-Coder-32B Model](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF) | 18 GB                  | Yes         |
| **Qwen 2.5 Coder 14B** | Q4_K_M  | [Qwen2.5-Coder-14B Model](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF) | 18 GB                  | Yes         |
| **Hermes LLAMA 3.1**   | Q4_K_M  | [LLAMA Model](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF)          | 12 GB                  | Yes         |

This table provides the **model name**, a **link** to the model, and the **GPU memory requirements** for each model. Ensure your hardware or cloud setup meets these requirements for inference or training.

---

## **2. Project Setup**

### **Prerequisites**

* **Python 3.10 or above**
* **pip** (Python package manager)
* **Conda (Optional)** if preferred for managing environments
* **sudo/root privileges** for installing system dependencies
* **Django App Database**: Follow the database setup instructions in the app’s own `setup.md` to configure and connect your preferred database.

---

## **INSTALLATION**

### **Step 1: Verify Python Installation**

Check your Python version:

```bash
python3 --version
```

If the version is earlier than 3.10, install the correct version (on Ubuntu):

```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip
```

---

### **Step 2: Choose Environment Setup**

#### Set Up a Virtual Environment with `venv`

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

   > **Note:** If there are issues with Python versions, specify version explicitly:

   ```bash
   python3.10 -m venv venv
   ```

2. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

---

### **Step 3: Install Dependencies**

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright and browser binaries:

   ```bash
   python3 -m playwright install
   ```

   This installs Chromium, Firefox, and WebKit.

---

### **Step 4: Set Up the Environment File (Only if You Don't Have One Already)**

1. Create the `.env` file:

   ```bash
   touch .env
   ```

2. Add the required environment variables:

   ```env
   # Can be "serverless", "local", or "openai"
   LLM_PROVIDER="local"

   # Local LLM Configuration
   #LOCAL_MODEL_ENDPOINT="http://192.168.0.103:6000/generate"
   LOCAL_MODEL_ENDPOINT="http://69.55.141.126:10278/generate"

   # OpenAI Configuration
   OPENAI_API_KEY=""
   OPENAI_MODEL="gpt-4-32k-0613"
   OPENAI_MAX_TOKENS="2000"
   OPENAI_TEMPERATURE="0.7"
   ```

3. Verify environment variables:

   ```bash
   cat .env
   ```

## **Step 5: Test Browser User Profile Through Login**

---

### **Step 5: Test Browser User Profile Through Login**

This script tests browser automation with a persistent user profile.

1. **Setup and Launch**: Loads the user profile directory and launches Chromium with saved session data (or creates a new profile).
2. **Authentication Check**: Logs in or registers if no session is found.
3. **Event Processing**: Retrieves events, saves them to the database, optionally deletes them.
4. **Clean Up**: Closes the browser after completing operations.

---

## **Notes**

1. **Environment Activation**:

   * For `venv`, run: `source venv/bin/activate` before starting development.

2. **Playwright Browsers**:
   Reinstall browsers if needed:

   ```bash
   python3 -m playwright install
   ```

   or

   ```bash
   playwright install
   ```

3. **Dependencies**:
   If dependencies change, update `requirements.txt`:

   ```bash
   pip freeze > requirements.txt
   ```

---

Your project should now be ready to run. If you encounter any issues, review the steps or consult the project documentation.
