#!/bin/bash

# Get list of windows from hyprland
# Format: [address] title (class)
windows=$(hyprctl clients -j | jq -r '.[] | "[\(.address)] \(.title) (\(.class))"')

if [ -z "$windows" ]; then
    echo "NO_ACTIVE_CORES" | rofi -dmenu -theme cyber_clean
    exit 1
fi

# Select window to kill
selected=$(echo "$windows" | rofi -dmenu -p "KILL_PROCESS" -theme cyber_clean)

if [ -n "$selected" ]; then
    # Extract address
    addr=$(echo "$selected" | awk -F'[][]' '{print $2}')
    hyprctl dispatch closewindow "address:$addr"
fi
