#!/bin/bash

# Get CPU usage
cpu_usage=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {printf "%0.1f%%", usage}')

# Get RAM usage
ram_info=$(free -m | awk 'NR==2{printf "%s/%s MB", $3,$2}')

# Get Uptime
uptime_str=$(uptime -p | sed 's/up //')

# Get Battery
if [ -d /sys/class/power_supply/BAT0 ]; then
    battery_level=$(cat /sys/class/power_supply/BAT0/capacity)%
else
    battery_level="N/A"
fi

# Get GPU (simple check for nvidia/intel/amd)
if command -v nvidia-smi &> /dev/null; then
    gpu_info=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)%
elif [ -d /sys/class/drm/card0/device/hwmon ]; then
    # Very basic placeholder for others
    gpu_info="LOADED"
else
    gpu_info="N/A"
fi

# Network
net_interface=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -n "$net_interface" ]; then
    net_status="ONLINE ($net_interface)"
else
    net_status="OFFLINE"
fi

echo "-------------------------------------"
echo "  [ IDENTITY ] $(whoami | tr '[:lower:]' '[:upper:]')"
echo "  [ SYSTEM   ] $(grep '^NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"' | tr '[:lower:]' '[:upper:]')"
echo "  [ CORE     ] ${XDG_CURRENT_DESKTOP:-HYPRLAND}"
echo "  [ UPTIME   ] ${uptime_str^^}"
echo "-------------------------------------"
echo "  [ CPU_LOAD ] $cpu_usage"
echo "  [ MEM_USED ] $ram_info"
echo "  [ GPU_LOAD ] $gpu_info"
echo "  [ ENERGY   ] $battery_level"
echo "-------------------------------------"
echo "  [ COMM_CH  ] $net_status"
echo "-------------------------------------"
echo "  SYSTEM_LINK : CODE7X_ULTRA_CORE"
echo "  SECURITY    : LEVEL_OMEGA_[⚡]"
