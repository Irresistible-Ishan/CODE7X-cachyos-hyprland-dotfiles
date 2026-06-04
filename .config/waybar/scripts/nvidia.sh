#!/bin/bash

MODE=$(supergfxctl -g)

if [[ "$MODE" == "Integrated" ]]; then
    echo '{"text":"","class":"hidden"}'
    exit 0
fi

UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null)
TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null)

echo "{\"text\":\"${UTIL}% ${TEMP}°C\",\"class\":\"nvidia\"}"
