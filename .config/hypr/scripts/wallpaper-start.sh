#!/bin/bash

mkdir -p ~/.cache/awww

pgrep awww-daemon >/dev/null || awww-daemon &

sleep 2

WALL=$(find ~/Wallpapers -type f | shuf -n 1)

awww img "$WALL"
