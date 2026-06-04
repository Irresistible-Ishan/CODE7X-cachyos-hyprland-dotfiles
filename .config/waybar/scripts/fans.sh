#!/bin/bash
cpu_fan=$(sensors | grep "cpu_fan" | awk '{print $2}')
gpu_fan=$(sensors | grep "gpu_fan" | awk '{print $2}')

# Fallback to 0 if empty
if [ -z "$cpu_fan" ]; then cpu_fan="0"; fi
if [ -z "$gpu_fan" ]; then gpu_fan="0"; fi

echo "{\"text\": \"󰈐 <span font_size='9pt'>CPU $cpu_fan</span>\\n<span font_size='9pt'>GPU $gpu_fan</span>\", \"class\": \"fans\"}"
