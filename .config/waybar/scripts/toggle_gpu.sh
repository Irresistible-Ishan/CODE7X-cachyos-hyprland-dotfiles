#!/bin/bash

MODE=$(supergfxctl -g)

if [[ "$MODE" == "Integrated" ]]; then
    supergfxctl -m Hybrid
    notify-send "DGPU" "RTX enabled. Logout required."
else
    supergfxctl -m Integrated
    notify-send "DGPU" "RTX disabled. Logout required."
fi
