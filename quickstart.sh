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
if ! command_exists python3 ; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Clone the repository
git clone https://github.com/victor-gurbani/terminal-wrapped.git
cd terminal-wrapped || exit

# Create virtual environment
python3 -m venv venv

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