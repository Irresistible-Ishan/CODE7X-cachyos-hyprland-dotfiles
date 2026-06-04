#!/bin/bash

CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print int($2)}')
TEMP=$(sensors | grep 'Package id 0:' | awk '{print int($4)}' | tr -d '+°C')

echo "{\"text\": \"󰍛 ${CPU}% ${TEMP}°C\", \"class\": \"cpuinfo\"}"
