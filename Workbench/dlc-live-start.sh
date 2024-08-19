#!/bin/bash

WORKING_DIR="/Users/cnl/Desktop/XBI_GazeML/"

# Open the first terminal window, activate the conda environment, and run the first Python script
osascript -e 'tell application "Terminal"
    do script "cd '$WORKING_DIR' && conda activate dlc-live && python3 DLCLive-Test.py"
end tell'

sleep 10

# Open the second terminal window and run the second Python script
osascript -e 'tell application "Terminal"
    do script "cd '$WORKING_DIR' && python3 server.py"
end tell'
