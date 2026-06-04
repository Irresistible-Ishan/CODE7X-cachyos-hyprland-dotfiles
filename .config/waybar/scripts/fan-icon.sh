#!/bin/bash
cpu_fan=$(sensors | awk '/cpu_fan/ {print $2}')
gpu_fan=$(sensors | awk '/gpu_fan/ {print $2}')

[ -z "$cpu_fan" ] && cpu_fan="0"
[ -z "$gpu_fan" ] && gpu_fan="0"

max_rpm=$(( cpu_fan > gpu_fan ? cpu_fan : gpu_fan ))

if [ "$max_rpm" -gt 2500 ]; then
    class="fast"
elif [ "$max_rpm" -gt 0 ]; then
    class="moving"
else
    class="stopped"
fi

echo "{\"text\": \"󰈐\", \"class\": \"$class\"}"
