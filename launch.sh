#!/bin/bash
# DMX Visualizer Control - Launch Script

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Qt platform for Steam Deck
export QT_QPA_PLATFORM=xcb
export SDL_GAMECONTROLLERCONFIG=""

# Launch the app
python3 main.py "$@"
