#!/bin/bash

while true; do
    WALL=$(find ~/Wallpapers -type f | shuf -n 1)
    awww img "$WALL"
    sleep 1800
done
