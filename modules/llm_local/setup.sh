#!/bin/bash

# **Setup Script for LLM Environment**
# This script sets up a Python environment, installs necessary dependencies, and starts a local LLM service using PM2.

# Step 1: Create and activate a Python virtual environment
echo "Creating and activating virtual environment..."
apt update -y && apt upgrade -y && apt install -y sudo
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-dev python3.10 python3.10-venv build-essential cmake wget
python3.10 -m venv venv_llm && source venv_llm/bin/activate

# Step 2: Download the model file from Hugging Face
# For testing of installation, commented it
echo "Downloading model file from Hugging Face..."
wget https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF/resolve/main/qwen2.5-coder-14b-instruct-q4_k_m.gguf

# Step 3: Set environment variables for CUDA and CMake
echo "Setting environment variables for CUDA and CMake..."
export CUDA_VERSION=cu121
export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
export FORCE_CMAKE=1

# Step 4: Install the llama-cpp-python package for GPU support
echo "Installing llama-cpp-python..."
pip install --no-cache-dir llama-cpp-python==0.2.90 --extra-index-url "https://abetlen.github.io/llama-cpp-python/whl/$CUDA_VERSION"

# Step 5: Install project dependencies from local_llm_requirements.txt
echo "Installing project dependencies from requirements.txt..."
pip install Flask==3.1.0 Flask_Cors==4.0.2 requests==2.32.3

# Step 6: Install and configure PM2 service for background management
echo "Installing and configuring PM2 service..."
sudo apt install -y npm
sudo npm install pm2 -g
pm2 update -y

