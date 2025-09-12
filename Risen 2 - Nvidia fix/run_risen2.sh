#!/usr/bin/env bash
# Run Risen 2 – Dark Waters under your Heroic prefix, offloading to NVIDIA

# 1) Point to your Heroic Wine/Proton prefix:
export WINEPREFIX="$HOME/Games/Heroic/Prefixes/default/Risen 2 Dark Waters/pfx"

# 2) Force prime-offload to your NVIDIA GPU:
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export __VK_LAYER_NV_optimus=1

# (Optional) Show DXVK HUD in the corner:
# export DXVK_HUD=fps,gpu,mem

# 3) cd into the game’s system folder and launch:
cd "$HOME/Games/Heroic/Risen 2 - Dark Waters/system"
exec wine "Risen.exe"
