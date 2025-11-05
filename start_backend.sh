#!/bin/bash

# Start script for Computer Investigations Framework

echo "Starting Computer Investigations Framework..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start backend server
echo "Starting backend server..."
python backend/server.py

