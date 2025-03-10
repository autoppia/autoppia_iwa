#!/bin/bash

# Usage: setup.sh [-l] [-w]
#   -l    Deploy LLM model (runs modules/setup.sh)
#   -w    Deploy demo webs using Docker Compose (runs modules/webs_demo/setup.sh)

set -e  # Exit immediately on error

DEPLOY_LLM=false
DEPLOY_WEBS=false

while getopts "lw" opt; do
    case "$opt" in
        l) DEPLOY_LLM=true ;;
        w) DEPLOY_WEBS=true ;;
        *) echo -e "\e[31m[ERROR]\e[0m Invalid option. Usage: $0 [-l] [-w]"; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

# Function to handle errors
function handle_error {
    echo -e "\e[31m[ERROR]\e[0m $1" >&2
    exit 1
}

# Function to print success messages
function success_msg {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

# Step 1: Install System Dependencies
echo -e "\e[34m[INFO]\e[0m Installing system dependencies..."
apt update -y && sudo apt upgrade -y || handle_error "System update failed"
apt install -y sudo || handle_error "Failed to install sudo"
sudo apt-get update -y && sudo apt-get upgrade -y

# Install Python 3.11 and essential dependencies
echo -e "\e[34m[INFO]\e[0m Installing Python 3.11 and dependencies..."
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get install -y \
  python3.11 python3.11-venv python3.11-dev build-essential cmake wget sqlite \
  libnss3 libnss3-dev libasound2 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
  libxrandr2 libgbm1 libpango-1.0-0 libatk-bridge2.0-0 libgtk-3-0 \
  libvpx-dev libevent-dev libopus0 libgstreamer1.0-0 unzip \
  libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 \
  libgstreamer-plugins-bad1.0-0 libwebp-dev libharfbuzz-dev \
  libsecret-1-dev libhyphen0 libflite1 libgles2-mesa libx264-dev libgtk-4-bin \
  libgtk-4-common libgtk-4-dev libgtk-4-1 libgraphene-1.0-0 \
  libgraphene-1.0-dev libwoff1 libgstreamer-gl1.0-0 libavif13 libenchant-2-2 \
  libmanette-0.2-0 || handle_error "Failed to install system dependencies"

# Step 2: Install `uv`
if ! command -v uv &> /dev/null; then
    echo -e "\e[34m[INFO]\e[0m Installing uv (Python package manager)..."
    curl -L https://astral.sh/uv/install.sh | sh || handle_error "Failed to install uv"
    export PATH="$HOME/.local/bin:$PATH"
    success_msg "uv installed successfully."
else
    echo -e "\e[32m[INFO]\e[0m uv already installed. Skipping."
fi

# Step 3: Verify Python 3.11 Installation
python3.11 --version || handle_error "Python 3.11 not found"

# Step 4: Create Virtual Environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\e[34m[INFO]\e[0m Creating virtual environment..."
    uv venv --python=3.11 || handle_error "Failed to create virtual environment"
    success_msg "Virtual environment created."
else
    echo -e "\e[32m[INFO]\e[0m Virtual environment already exists. Skipping."
fi

# Step 5: Activate Virtual Environment
echo -e "\e[34m[INFO]\e[0m Activating virtual environment..."
source "$VENV_DIR/bin/activate" || handle_error "Failed to activate virtual environment"

# Step 6: Upgrade pip & setuptools
echo -e "\e[34m[INFO]\e[0m Upgrading pip and setuptools..."
python3.11 -m ensurepip
uv pip install --upgrade pip setuptools || handle_error "Failed to upgrade pip and setuptools"
success_msg "pip and setuptools upgraded successfully."

# Step 7: Install Python Dependencies
echo -e "\e[34m[INFO]\e[0m Installing Python dependencies..."
uv pip install -e . || handle_error "Failed to install dependencies"
success_msg "Python dependencies installed."

# Step 8: Install Playwright & Browser Binaries
echo -e "\e[34m[INFO]\e[0m Installing Playwright..."
playwright install || handle_error "Failed to install Playwright browsers"
success_msg "Playwright installed successfully."

# Step 9: Deploy LLM Model (if selected)
if [ "$DEPLOY_LLM" = true ]; then
    echo -e "\e[34m[INFO]\e[0m Deploying LLM model..."
    cd modules || handle_error "Failed to change directory to modules"
    sudo chmod +x setup.sh && bash setup.sh || handle_error "LLM setup script failed"
    cd .. || handle_error "Failed to return to autoppia_iwa root"
    success_msg "LLM model deployed successfully."
else
    echo -e "\e[32m[INFO]\e[0m Skipping LLM model deployment."
fi

# Step 10: Deploy Demo Webs using Docker Compose (if selected)
if [ "$DEPLOY_WEBS" = true ]; then
    echo -e "\e[34m[INFO]\e[0m Deploying demo webs using Docker Compose..."
    cd modules/webs_demo || handle_error "Failed to change directory to modules/webs_demo"
    sudo chmod +x setup.sh && bash setup.sh || handle_error "Webs demo setup failed"
    cd ../.. || handle_error "Failed to return to autoppia_iwa root"
    success_msg "Demo webs deployed successfully."
else
    echo -e "\e[32m[INFO]\e[0m Skipping demo webs deployment."
fi

echo -e "\e[32m[SUCCESS]\e[0m Installation and setup complete!"
