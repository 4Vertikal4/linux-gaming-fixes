# Horizon Forbidden West Complete Edition - Audio Fix & Shader Tweaks (Heroic/Epic)

## The Issue
On systems like Fedora (Rawhide/42) using **Heroic Games Launcher (Flatpak)**, users may experience the following behavior:

1.  **Cold Boot Lag:** The first launch takes a significant amount of time due to heavy shader compilation.
2.  **Audio Failure (Launch):** Often, after loading, the game starts with **no audio**.
3.  **Audio Failure (Fast Travel):** Sound may cut out specifically after using Fast Travel to a new biome, causing a CPU spike due to new shader compilation.

The audio failure is caused by the sound server (PipeWire/PulseAudio) timing out while the CPU is 100% utilized by shader compilation (VKD3D/DX12).

## The Fix

The fix involves significantly increasing audio latency tolerance and optimizing shader caching storage to prevent constant recompilation.

### 1. Heroic Settings
Go to **Game Settings** -> **Advanced**.

### 2. Environment Variables
Add the following variables to the "Environment Variables" section.

> **Warning:** Do NOT put terminal commands (like `ulimit`) in this section. It will break the launch process.

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PROTON_AUDIO_BACKEND` | `pipewire` | Forces the correct audio backend. |
| `PULSE_LATENCY_MSEC` | `300` | **THE FIX:** Sets audio latency tolerance to 300ms. Prevents sound death during heavy load spikes (Launch & Fast Travel). |
| `PROTON_EAC_RUNTIME` | `1` | Helps with Easy Anti-Cheat compatibility environment. |
| `VKD3D_CONFIG` | `pipeline_library_app_cache,skip_cleanup` | Optimizes DX12 shader pipeline and prevents cache deletion. |
| `VKD3D_SHADER_CACHE_PATH` | `/home/vertikal/Games/Heroic/Shaders` | **User defined path:** Keeps DX12 caches safe from updates/wipes. |
| `__GL_SHADER_DISK_CACHE` | `1` | Enables Nvidia disk cache. |
| `__GL_SHADER_DISK_CACHE_PATH` | `/home/vertikal/Games/Heroic/Shaders` | **User defined path:** Stores Nvidia GL cache in the safe folder. |
| `__GL_SHADER_DISK_CACHE_SIZE` | `10000` | Sets Nvidia cache size to 10GB (default is often too small for HFW). |
| `__GL_SHADER_DISK_CACHE_SKIP_CLEANUP` | `1` | Prevents Nvidia driver from deleting older shaders. |

### 3. Other Settings
*   **GameMode:** Enable "Use GameMode" (check the box).
*   **Wine Version:** Use the latest **GE-Proton** (e.g., GE-Proton9-23 or newer).

## Verified System Spec
The fix was confirmed working on the following configuration:

*   **OS:** Fedora Linux 42 (Workstation Edition) - Flatpak Runtime
*   **CPU:** 12th Gen Intel(R) Core(TM) i5-12400F (12 Threads)
*   **GPU:** NVIDIA GeForce RTX 3060 Ti LHR
*   **RAM:** 32 GB
*   **Driver:** NVIDIA Proprietary
*   **Launcher:** Heroic Games Launcher 2.18.1 "Waterfall Beard"
