#!/bin/bash
# Start PS-03 API Server

echo "Starting PS-03 API Server..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start API
python api/main.py
