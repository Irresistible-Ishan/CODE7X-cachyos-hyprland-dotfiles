#!/bin/bash
cpu_fan=$(sensors | awk '/cpu_fan/ {print $2}')
gpu_fan=$(sensors | awk '/gpu_fan/ {print $2}')

[ -z "$cpu_fan" ] && cpu_fan="0"
[ -z "$gpu_fan" ] && gpu_fan="0"

echo "{\"text\": \"<span font_size='9pt' rise='1000'>CPU: $cpu_fan RPM</span>\\n<span font_size='9pt' rise='-1000'>GPU: $gpu_fan RPM</span>\", \"class\": \"fan-text\"}"