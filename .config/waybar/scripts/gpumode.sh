#!/bin/bash

MODE=$(supergfxctl -g)

if [[ "$MODE" == "Integrated" ]]; then
    echo '{"text":"󰖳 DGPU OFF","class":"gpuoff"}'
else
    echo '{"text":"󰢮 DGPU ON","class":"gpuon"}'
fi
