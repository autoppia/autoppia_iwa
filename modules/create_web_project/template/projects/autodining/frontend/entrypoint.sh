#!/bin/sh
set -e

# --- Configuration Variables ---
NODE_VERSION="v20"
APP_NAME="autodining-app"
APP_PORT="8003"
APP_HOST="0.0.0.0"
NVM_INSTALL_SCRIPT="https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh"


log_message() {
  echo ">>> $1"
}

error_exit() {
  echo "!!! ERROR: $1" >&2
  exit 1
}

# --- Pre-flight Checks ---

log_message "Starting Next.js application deployment..."

# Check for curl
if ! command -v curl >/dev/null 2>&1; then
  error_exit "curl is not installed. Please install it to proceed."
fi

# Check for npm
if ! command -v npm >/dev/null 2>&1; then
  error_exit "npm is not installed. This script requires npm."
fi

# Check for pm2
if ! command -v pm2 >/dev/null 2>&1; then
  log_message "PM2 not found. Please install PM2 globally: 'npm install -g pm2'."
  error_exit "PM2 is not installed or not in PATH."
fi

# --- NVM Installation and Setup ---

if [ ! -d "$HOME/.nvm" ]; then
  log_message "NVM not found. Installing NVM..."
  curl -o- "$NVM_INSTALL_SCRIPT" | bash || error_exit "Failed to install NVM."
else
  log_message "NVM already installed."
fi

# Load NVM (ensure this works in both login and non-login shells)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"

# Verify NVM loaded
if ! command -v nvm >/dev/null 2>&1; then
  error_exit "NVM failed to load. Check NVM installation."
fi

# Install and use the specified Node.js version
log_message "Installing and using Node.js $NODE_VERSION (latest patch version)..."
nvm install "$NODE_VERSION" || error_exit "Failed to install Node.js $NODE_VERSION."
nvm use "$NODE_VERSION" || error_exit "Failed to use Node.js $NODE_VERSION."
nvm alias default "$NODE_VERSION" || error_exit "Failed to set default Node.js version."

# Print Node and NPM versions for verification
log_message "Node.js version: $(node -v)"
log_message "NPM version: $(npm -v)"

# --- Application Preparation ---

# Clean build artifacts (but not node_modules)
log_message "Cleaning build artifacts..."
rm -rf .next out package-lock.json || log_message "No .next, out, or package-lock.json to remove."

# Reinstall dependencies
log_message "Reinstalling Node.js dependencies..."
npm install || error_exit "Failed to install Node.js dependencies."

# Build the Next.js app for production (important!)
log_message "Building the Next.js application for production..."
npm run build || error_exit "Failed to build the Next.js application. Please resolve compilation errors."

# --- PM2 Management ---

log_message "Checking for existing PM2 process '$APP_NAME'..."
if pm2 describe "$APP_NAME" > /dev/null 2>&1; then
  log_message "Stopping and deleting existing PM2 process '$APP_NAME'..."
  pm2 stop "$APP_NAME" && pm2 delete "$APP_NAME" || log_message "Failed to stop/delete PM2 process, but continuing."
else
  log_message "No existing PM2 process '$APP_NAME' found."
fi

# Start the app using PM2
log_message "Starting the Next.js application with PM2 on port $APP_PORT..."
# Using 'npm run start' after 'npm run build' is the correct way for Next.js production.
pm2 start npm --name "$APP_NAME" -- run start -- -p "$APP_PORT" -H "$APP_HOST" || error_exit "Failed to start application with PM2."

# Save PM2 process list and enable startup on boot
log_message "Saving PM2 process list and enabling startup on boot..."
pm2 save || log_message "Failed to save PM2 process list. Manual save might be needed."

log_message "Deployment completed successfully. Application '$APP_NAME' should be running on http://$APP_HOST:$APP_PORT"
pm2 list
