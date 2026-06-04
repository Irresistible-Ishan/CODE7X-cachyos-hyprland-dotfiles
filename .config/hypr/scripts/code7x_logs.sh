#!/bin/bash

# Generates a "Tactical Log" or "Neural Uplink" feed for the bottom left
lines=6
log_pool=(
    "INITIATING_NEURAL_UPLINK..."
    "SYNCING_SYNAPTIC_DRIVES..."
    "MEMORY_DUMP_AT_0x${RANDOM%9}F${RANDOM%9}A..."
    "GHOST_IN_THE_SHELL_DETECTED..."
    "UPDATING_TACTICAL_MAP..."
    "ENCRYPTING_BIO_SIGNAL..."
    "BYPASSING_LOCAL_FIREWALL..."
    "ACCESSING_SATELLITE_LINK..."
    "BUFFER_OVERFLOW_PREVENTED."
    "SYSTEM_STABILITY: 99.9%"
    "NEURAL_LATENCY: 4ms"
    "OVERRIDING_CORE_PROTOCOL..."
)

for ((i=0; i<$lines; i++)); do
    idx=$((RANDOM % ${#log_pool[@]}))
    echo " > ${log_pool[$idx]}"
done
