#!/bin/bash
WALL=$(find ~/Wallpapers -type f \( -iname '*.jpg' -o -iname '*.png' -o -iname '*.webp' -o -iname '*.jpeg' \) | shuf -n 1)
if [ -n "$WALL" ]; then
    awww img "$WALL"
fi
