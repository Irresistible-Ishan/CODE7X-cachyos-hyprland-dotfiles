#!/bin/bash

# A simple script to generate a rotating "data stream" or symbols
symbols=("◢" "◣" "◤" "◥" "░" "▒" "▓" "█" "▲" "▼" "◀" "▶" "◆" "◇" "○" "◎" "●" "◐" "◑" "◒" "◓" "◔" "◕" "◖" "◗")
length=40
output=""

for ((i=0; i<$length; i++)); do
    idx=$((RANDOM % ${#symbols[@]}))
    output+="${symbols[$idx]}"
done

# Glitch effect: occasionally insert "CODE7X" or "LOCKED"
if (( RANDOM % 5 == 0 )); then
    pos=$(( RANDOM % (length - 6) ))
    output="${output:0:pos}CODE7X${output:pos+6}"
fi

echo "$output"
