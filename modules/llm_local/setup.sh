
echo "Creating and activating virtual environment..."
apt update -y && apt upgrade -y && apt install -y sudo
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-dev python3.10 python3.10-venv build-essential cmake wget
python3.10 -m venv llm_env && source llm_env/bin/activate
echo "Checking CUDA installation..."

# Check if CUDA is installed
if ! command -v nvcc &> /dev/null; then
    echo "❌ CUDA Toolkit not found. Installing..."
    
    # Add NVIDIA repository
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:graphics-drivers/ppa
    sudo apt-get update

    # Install CUDA (latest available from the repo)
    sudo apt-get install -y nvidia-cuda-toolkit

else
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -d',' -f1)
    echo "✅ CUDA Toolkit found: Version $CUDA_VERSION"
fi

MODEL_FILE="qwen2.5-coder-14b-instruct-q4_k_m.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "Downloading model file from Hugging Face..."
    wget https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF/resolve/main/$MODEL_FILE
else
    echo "Model file '$MODEL_FILE' already exists, skipping download."
fi

echo "Setting environment variables for CUDA and CMake..."
export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
export FORCE_CMAKE=1

echo "Installing llama-cpp-python..."
pip install --no-cache-dir llama-cpp-python==0.2.90 --extra-index-url "https://abetlen.github.io/llama-cpp-python/whl/cu121"

echo "Installing project dependencies from local_llm_requirements.txt..."
pip install -r autoppia_iwa_module/modules/llm_local/requirements.txt

echo "Installing and configuring PM2 service..."
sudo apt install -y npm
sudo npm install pm2 -g
pm2 update -y
