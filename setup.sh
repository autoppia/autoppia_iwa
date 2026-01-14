#!/bin/bash

# Usage: setup.sh [-w]
#   -w    Deploy demo webs using Docker Compose (runs modules/webs_demo/setup.sh)

set -Eeuo pipefail
IFS=$'\n\t'

# Determine privilege helper
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        echo -e "\e[31m[ERROR]\e[0m This script requires root privileges or sudo. Please run as root or install sudo." >&2
        exit 1
    fi
fi

DEPLOY_WEBS=false

while getopts "w" opt; do
    case "$opt" in
        w) DEPLOY_WEBS=true ;;
        *) echo -e "\e[31m[ERROR]\e[0m Invalid option. Usage: $0 [-w]"; exit 1 ;;
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
export DEBIAN_FRONTEND=noninteractive
echo -e "\e[34m[INFO]\e[0m Installing system dependencies..."
$SUDO apt-get update -y || handle_error "System update failed (update)"
$SUDO apt-get upgrade -y || handle_error "System update failed (upgrade)"

# Install Python 3.11 and essential dependencies
echo -e "\e[34m[INFO]\e[0m Installing base packages and libraries..."

# Detect Ubuntu version for package name compatibility
if [ -f /etc/os-release ]; then
  . /etc/os-release
  UBUNTU_VERSION=$(echo "$VERSION_ID" | cut -d. -f1)
else
  UBUNTU_VERSION="22"
fi

# Use t64 packages for Ubuntu 24.04+ (transición arquitectura)
if [ "$UBUNTU_VERSION" -ge 24 ]; then
  ASOUND_PKG="libasound2t64"
  GLES_PKG="libgles2"
  AVIF_PKG="libavif16"
else
  ASOUND_PKG="libasound2"
  GLES_PKG="libgles2-mesa"
  AVIF_PKG="libavif13"
fi

$SUDO apt-get install -y \
  ca-certificates curl git unzip tar wget sqlite3 pkg-config \
  build-essential cmake \
  libnss3 libnss3-dev "$ASOUND_PKG" libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
  libxrandr2 libgbm1 libpango-1.0-0 libgtk-3-0 \
  libvpx-dev libevent-dev libopus0 libgstreamer1.0-0 \
  libgstreamer-plugins-base1.0-0 libgstreamer-plugins-good1.0-0 \
  libgstreamer-plugins-bad1.0-0 libwebp-dev libharfbuzz-dev \
  libsecret-1-dev libhyphen0 libflite1 "$GLES_PKG" libx264-dev libgtk-4-bin \
  libgtk-4-common libgtk-4-dev libgtk-4-1 libgraphene-1.0-0 \
  libgraphene-1.0-dev libwoff1 libgstreamer-gl1.0-0 "$AVIF_PKG" libenchant-2-2 \
  libmanette-0.2-0 || handle_error "Failed to install base dependencies"

# Ensure Python >= 3.11
PYTHON_BIN=""
ensure_python() {
  # Prefer already-installed Python 3.11, then 3.13/3.12
  for ver in 3.11 3.13 3.12; do
    if command -v python$ver >/dev/null 2>&1; then
      PYTHON_BIN="python$ver"
      return 0
    fi
  done
  # Try to install via apt
  for ver in 3.11 3.13 3.12; do
    echo -e "\e[34m[INFO]\e[0m Attempting to install python$ver..."
    if $SUDO apt-get install -y python$ver python$ver-venv python$ver-dev; then
      PYTHON_BIN="python$ver"
      return 0
    fi
  done
  # Try deadsnakes PPA for Ubuntu/Debian
  if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get install -y software-properties-common || true
    if command -v add-apt-repository >/dev/null 2>&1; then
      $SUDO add-apt-repository -y ppa:deadsnakes/ppa || true
      $SUDO apt-get update -y || true
      # Prefer 3.11 first, then 3.12
      if $SUDO apt-get install -y python3.11 python3.11-venv python3.11-dev || \
         $SUDO apt-get install -y python3.12 python3.12-venv python3.12-dev; then
        if command -v python3.11 >/dev/null 2>&1; then
          PYTHON_BIN="python3.11"
        else
          PYTHON_BIN="python3.12"
        fi
        return 0
      fi
    fi
  fi
  # As a last resort, use system python3 if it satisfies >=3.12
  if command -v python3 >/dev/null 2>&1; then
    if python3 -c 'import sys; import sys; sys.exit(0 if sys.version_info[:2] >= (3,11) else 1)'; then
      PYTHON_BIN="python3"
      $SUDO apt-get install -y python3-venv python3-dev || true
      return 0
    fi
  fi
  return 1
}

echo -e "\e[34m[INFO]\e[0m Checking/Installing Python (>= 3.11)..."
ensure_python || handle_error "Python 3.11+ is required. Unable to install automatically."
"$PYTHON_BIN" --version || true

# Step 2: Install `uv`
if ! command -v uv &> /dev/null; then
    echo -e "\e[34m[INFO]\e[0m Installing uv (Python package manager)..."
    curl -fsSL https://astral.sh/uv/install.sh | sh || handle_error "Failed to install uv"
    export PATH="$HOME/.local/bin:$PATH"
    success_msg "uv installed successfully."
else
    echo -e "\e[32m[INFO]\e[0m uv already installed. Skipping."
fi

# Step 3: Verify Python Installation
"$PYTHON_BIN" --version || handle_error "Python not found after installation"
"$PYTHON_BIN" -c 'import sys; assert sys.version_info[:2] >= (3,11), "Python 3.11+ required"' || handle_error "Python version must be >= 3.11"

# Step 4: Create Virtual Environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\e[34m[INFO]\e[0m Creating virtual environment..."
    uv venv --python="$PYTHON_BIN" || handle_error "Failed to create virtual environment"
    success_msg "Virtual environment created."
else
    echo -e "\e[32m[INFO]\e[0m Virtual environment already exists. Skipping."
fi

# Step 5: Activate Virtual Environment
echo -e "\e[34m[INFO]\e[0m Activating virtual environment..."
source "$VENV_DIR/bin/activate" || handle_error "Failed to activate virtual environment"

# Step 6: Upgrade pip & setuptools
echo -e "\e[34m[INFO]\e[0m Upgrading pip, setuptools and wheel..."
"$PYTHON_BIN" -m ensurepip || true
uv pip install --upgrade pip setuptools wheel || handle_error "Failed to upgrade pip/setuptools/wheel"
success_msg "pip, setuptools and wheel upgraded successfully."

# Step 7: Install Python Dependencies
echo -e "\e[34m[INFO]\e[0m Installing Python dependencies..."
uv pip install -r requirements.txt || handle_error "Failed to install requirements.txt dependencies"
uv pip install -e . || handle_error "Failed to install project (editable)"
success_msg "Python dependencies installed."

# Step 8: Install Playwright & Browser Binaries
echo -e "\e[34m[INFO]\e[0m Installing Playwright..."
if ! playwright install --with-deps; then
    echo -e "\e[33m[WARN]\e[0m 'playwright install --with-deps' failed, retrying with 'playwright install'"
    playwright install || handle_error "Failed to install Playwright browsers"
fi
success_msg "Playwright installed successfully."

# Step 9: Deploy Demo Webs using Docker Compose (if selected)
if [ "$DEPLOY_WEBS" = true ]; then
    echo -e "\e[34m[INFO]\e[0m Deploying demo webs using Docker Compose..."
    cd modules/webs_demo || handle_error "Failed to change directory to modules/webs_demo"
    $SUDO chmod +x setup.sh && bash setup.sh || handle_error "Webs demo setup failed"
    cd ../.. || handle_error "Failed to return to autoppia_iwa root"
    success_msg "Demo webs deployed successfully."
else
    echo -e "\e[32m[INFO]\e[0m Skipping demo webs deployment."
fi

echo -e "\e[32m[SUCCESS]\e[0m Installation and setup complete!"
