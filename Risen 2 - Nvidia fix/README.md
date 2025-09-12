# Risen 2 - Dark Waters - NVIDIA GPU Offloading Fix

## Problem Solved
Risen 2 - Dark Waters may experience performance issues or fail to utilize dedicated NVIDIA GPU when running through Heroic Games Launcher on Linux systems with hybrid graphics (Intel/NVIDIA).

## Solution
This bash script forces the game to run on the dedicated NVIDIA GPU using Prime offloading, ensuring better performance and stability during gameplay.

## Features
- Forces NVIDIA GPU usage via Prime render offload
- Configured for Heroic Games Launcher Wine/Proton prefix
- Optional DXVK HUD for monitoring FPS and GPU usage
- Improves overall game performance on hybrid graphics laptops

## Requirements
- NVIDIA GPU with proprietary drivers
- Heroic Games Launcher
- Wine/Proton compatible prefix
- Prime render offload support

## 🔧 Installation & Usage

### Step 1: Download the Script
Download `risen2-nvidia-fix.sh` to your system

### Step 2: Edit Paths
Edit the script to match your game installation paths:

```bash
# Update this line with your Heroic prefix path:
export WINEPREFIX="$HOME/Games/Heroic/Prefixes/default/Risen 2 Dark Waters/pfx"
```

### Update this line with your game installation directory:

```
cd "$HOME/Games/Heroic/Risen 2 - Dark Waters/system"
```

### Step 3: Make Executable
```bash
chmod +x risen2-nvidia-fix.sh
```

### Step 4: Run the Game
```
./risen2-nvidia-fix.sh
```

⚠️ Known Issue - Island Travel Bug
The Problem

When sailing between islands, the game may crash or freeze when using this script.

Workaround Steps

- Save your game before attempting to travel between islands
- Exit the game
- Launch Risen 2 without the script (through Heroic launcher normally)
- Complete the island travel sequence
- Save the game at the new location
- Exit and relaunch using the script for continued play

Tested Configuration

- OS: Fedora 41 and 42 Workstation
- CPU: 12th Gen Intel i5-12400F
- GPU: NVIDIA RTX 3060 Ti
- RAM: 16GB
- Heroic installation method: Flatpak (system-wide)
- Wine version: Wine-GE-Proton8-26. This solution should also work on the newer versions like: GE-Proton10-3 or higher.

## Script Overview

The script sets these environment variables:

**`WINEPREFIX`**  
Points to Heroic Wine/Proton prefix for the game

**`__NV_PRIME_RENDER_OFFLOAD`**  
Forces the system to use NVIDIA GPU for rendering

**`__GLX_VENDOR_LIBRARY_NAME`**  
Directs OpenGL to use NVIDIA libraries

**`__VK_LAYER_NV_optimus`**  
Enables Vulkan NVIDIA Optimus layer for better compatibility


Uncomment this line in the script to show performance metrics:
```
export DXVK_HUD=fps,gpu,mem
```

🤝 Contributing

If you find improvements or fixes for the island travel issue, please submit a pull request!

📄 License
This fix is provided as-is for the Linux gaming community. This fix provides a stable workaround for hybrid graphics users experiencing GPU utilization issues with Risen 2 on Linux.

