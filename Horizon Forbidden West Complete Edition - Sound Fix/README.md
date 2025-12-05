# Horizon Forbidden West Complete Edition - Sound & Long Loading Fix (Heroic Games Launcher)

## The Issue
On systems like Fedora (Rawhide/42) using **Heroic Games Launcher (Flatpak)**, the game exhibits specific behavior:
1.  **Cold Boot:** The first launch takes an extremely long time (~5 minutes), likely due to shader compilation. When the game finally starts, **there is no audio**.
2.  **Warm Boot:** Restarting the game immediately after makes it load instantly, and audio works correctly.

This issue is often caused by the audio server (PipeWire/PulseAudio) timing out during the heavy shader compilation process on the first launch.

## The Fix

The fix involves setting specific environment variables to handle audio latency and ensuring no syntax errors in the launcher configuration.

### 1. Heroic Settings
Go to **Game Settings** -> **Advanced**.

### 2. Environment Variables
Add the following variables to the "Environment Variables" section. 

> **Warning:** Do NOT put terminal commands (like `ulimit`) in this section. It will break the launch process.

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PROTON_AUDIO_BACKEND` | `pipewire` | Forces the correct audio backend. |
| `PULSE_LATENCY_MSEC` | `60` | **Crucial:** Increases audio latency tolerance, preventing sound dropouts during high CPU load (shader compilation). |
| `PROTON_EAC_RUNTIME` | `1` | Helps with Easy Anti-Cheat compatibility. |
| `__GL_SHADER_DISK_CACHE_SKIP_CLEANUP` | `1` | *(NVIDIA Only)* Prevents the driver from aggressively cleaning up the shader cache. |

### 3. Other Settings
*   **GameMode:** Enable "Use GameMode" (check the box). This automatically handles `ulimit` and CPU priorities better than manual commands.
*   **Wine Version:** Use the latest **GE-Proton** (e.g., GE-Proton9-20 or newer).

## Verified On
*   **OS:** Fedora 42 (Rawhide)
*   **Launcher:** Heroic Games Launcher (Flatpak v2.18.1+)
*   **GPU:** NVIDIA
*   **Audio Server:** PipeWire

<to be done> add system information from Heroic Games Launcher to the readme file.
