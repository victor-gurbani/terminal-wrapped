#!/usr/bin/env bash

# Terminal-Wrapped Quickstart Script
set -euo pipefail

echo "🚀 Starting Terminal-Wrapped Setup..."

# Function to check command existence
command_exists () {
    command -v "$1" >/dev/null 2>&1 ;
}

fail() {
    echo "Error: $1" >&2
    exit 1
}

# Check for git
if ! command_exists git ; then
    fail "git is not installed."
fi

# Check for Python 3
PYTHON_CMD=""
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    # Check if python is version 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    fail "Python 3 is not installed."
fi

# Clone or update the repository
if [ -d "terminal-wrapped" ]; then
    echo "Directory terminal-wrapped already exists. Updating..."
    cd terminal-wrapped || exit
    git pull --ff-only
else
    echo "Cloning repository..."
    git clone https://github.com/victor-gurbani/terminal-wrapped.git
    cd terminal-wrapped || exit
fi

# Create or reuse virtual environment
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

python -m pip install --upgrade pip setuptools wheel >/dev/null

# Install dependencies
if [ -f requirements.txt ]; then
    python -m pip install -r requirements.txt
else
    # If requirements.txt doesn't exist, install Flask manually
    python -m pip install flask
fi

# Run the main script
python main.py