#!/usr/bin/env bash

# Terminal-Wrapped Quickstart Script

# Function to check command existence
command_exists () {
    command -v "$1" >/dev/null 2>&1 ;
}

# Check for git
if ! command_exists git ; then
    echo "Error: git is not installed."
    exit 1
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
    echo "Error: Python 3 is not installed."
    exit 1
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

# Create virtual environment
$PYTHON_CMD -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    # If requirements.txt doesn't exist, install Flask manually
    pip install flask
fi

# Run the main script
python main.py