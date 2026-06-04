# Code7x Cyberpunk Dotfiles - CachyOS / Arch Linux (Wayland)

Welcome to my custom Hyprland dotfiles! This setup is highly customized for a Cyberpunk aesthetic, featuring custom-built GUI applications for wallpaper and note management, built entirely with Python and PyQt6. It is specifically tailored with hardware controls for the **ASUS TUF F15 (FX506HC)** but can be adapted for any system.

![Desktop Preview](.config/waybar/preview.png) *(Add your preview screenshot here!)*

## 🚀 Features

* **Window Manager:** [Hyprland](https://hyprland.org/) (Wayland)
* **Status Bar:** Custom [Waybar](https://github.com/Alexays/Waybar) with integrated controls.
* **App Launcher / Menus:** [Rofi](https://github.com/davatorium/rofi) (Cyberpunk-themed).
* **Terminal Environment:** Alacritty + Fish Shell + Fastfetch.
* **Wallpaper Manager (`code7x_gallery.py`):** A custom PyQt6 GUI application to browse, fetch, and apply wallpapers natively.
* **Sidebar / Notes App (`code7x_sidebar.py`):** A beautiful, custom PyQt6 sliding sidebar for note-taking directly accessible via Waybar.
* **ASUS TUF F15 Hardware Controls:** 
  * Custom Waybar modules for toggling the NVIDIA dGPU on/off.
  * Real-time dGPU and iGPU monitoring.
  * CPU/GPU fan speed monitoring and controls.
  * Brightness and power profile management.

## 📦 Requirements

* **OS:** CachyOS / Arch Linux
* **Dependencies:**
  * `hyprland` `waybar` `rofi-wayland` `alacritty` `fish` `fastfetch`
  * `python-pyqt6` (for the custom wallpaper and notes apps)
  * `grim` `slurp` `wl-clipboard` (for screenshots)
  * `cliphist` (for clipboard management)
  * `hypridle` `hyprlock`
  * GPU/Hardware specific drivers (e.g., `nvidia`, `asusctl` or `supergfxctl` depending on your specific kernel module choices).

## 🛠️ Installation

**1. Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/dotfiles.git ~/dotfiles
cd ~/dotfiles
```

**2. Run the install script:**
```bash
chmod +x install.sh
./install.sh
```
*Note: This script will back up your existing configurations before applying the new ones.*

## 💻 Custom App Highlights

### Code7x Gallery (Wallpaper Manager)
Accessed via `SUPER + W`, this is a fully custom-built Python/PyQt6 gallery that reads from `~/Wallpapers/Cyberpunk`, caches thumbnails, and sets wallpapers dynamically via Hyprland's ecosystem (e.g. `awww` or `hyprpaper`).

### Code7x Sidebar (Notes)
Click the `[ NOTE ]` module on Waybar to trigger `add_note.sh`, which interfaces with the custom PyQt6 sidebar widget. It seamlessly overlays on your desktop, giving you a beautiful quick-access notepad.

## 🎮 ASUS TUF Controls
The Waybar features specific scripts found in `~/.config/waybar/scripts/` such as `gpumode.sh`, `toggle_gpu.sh`, `fan-text.sh`, and `fan-icon.sh` which poll hardware sensors and provide one-click toggle capabilities directly on your bar. 

---
*Created by [Your Name/Handle]*
