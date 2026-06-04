#!/bin/bash
# Signal the sidebar to focus its input field
pkill -USR1 -f code7x_sidebar.py || python3 ~/.config/hypr/scripts/code7x_sidebar.py
