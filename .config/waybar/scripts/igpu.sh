#!/bin/bash

# Intel GPU usage estimation based on frequency
CUR=$(cat /sys/class/drm/card2/device/drm/card2/gt/gt0/rps_act_freq_mhz 2>/dev/null)
MAX=$(cat /sys/class/drm/card2/device/drm/card2/gt/gt0/rps_max_freq_mhz 2>/dev/null)

if [[ -n "$CUR" && -n "$MAX" && "$MAX" -gt 0 ]]; then
    USAGE=$(( CUR * 100 / MAX ))
else
    USAGE=0
fi

echo "{\"text\": \"󰒋 ${USAGE}%\", \"class\": \"igpu\"}"
