#!/bin/bash

# Simple install script for Code7x Dotfiles

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$HOME/.config_backup_$(date +%Y%m%d_%H%M%S)"

echo "🚀 Starting Code7x Dotfiles Installation..."
echo "📂 Backing up existing configs to $BACKUP_DIR"

mkdir -p "$BACKUP_DIR"

# List of configs to install
CONFIGS=("hypr" "waybar" "rofi" "fastfetch" "fish" "starship")

for config in "${CONFIGS[@]}"; do
    if [ -d "$HOME/.config/$config" ] || [ -f "$HOME/.config/$config" ]; then
        mv "$HOME/.config/$config" "$BACKUP_DIR/"
        echo "   -> Backed up $config"
    fi
    
    if [ -d "$DOTFILES_DIR/.config/$config" ]; then
        cp -r "$DOTFILES_DIR/.config/$config" "$HOME/.config/"
        echo "   -> Installed $config"
    fi
done

# Ensure python requirements are met (PyQt6 for custom apps)
echo "🐍 Checking for python dependencies (PyQt6)..."
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "   -> PyQt6 missing! Please install it via your package manager (e.g., sudo pacman -S python-pyqt6)"
fi

echo "✅ Installation complete! Please reload Hyprland (SUPER+M) or reboot your system."
