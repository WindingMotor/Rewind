#!/bin/bash

# Navigate to the directory
cd ~/Documents/autoc

# Activate the virtual environment
source autocomplete_env/bin/activate

# Run the capture.py script
python3 capture.py

# Deactivate the virtual environment
deactivate

# Send KDE notification
kdialog --passivepopup "Screenshot captured and processed" 2 --title "Rewind Memory Assistant"

# Exit the script
exit 0
