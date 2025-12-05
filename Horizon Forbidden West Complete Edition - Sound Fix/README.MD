# Horizon Forbidden West Complete Edition - Audio Fix & Shader Tweaks (Heroic/Epic)

## The Issue
On systems like Fedora (Rawhide/42) using **Heroic Games Launcher (Flatpak)**, users may experience the following behavior:

1.  **Cold Boot Lag:** The first launch takes a significant amount of time (can be up to 5+ minutes) due to heavy shader compilation/verification.
2.  **Audio Failure:** Often, after this long loading period, the game starts with **no audio**.
3.  **Warm Boot:** Restarting the game immediately usually results in a fast load with working audio.

The audio failure is caused by the sound server (PipeWire/PulseAudio) timing out while the CPU is 100% utilized by shader compilation during the initial launch.

## The Fix

The primary fix ensures the audio server waits longer for the game to respond during the heavy load. We also add tweaks to help with shader retention.

### 1. Heroic Settings
Go to **Game Settings** -> **Advanced**.

### 2. Environment Variables
Add the following variables to the "Environment Variables" section.

> **Warning:** Do NOT put terminal commands (like `ulimit`) in this section. It will break the launch process.

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PROTON_AUDIO_BACKEND` | `pipewire` | Forces the correct audio backend. |
| `PULSE_LATENCY_MSEC` | `60` | **THE FIX:** Increases audio latency tolerance. Prevents sound from dying during the long shader compilation phase. |
| `PROTON_EAC_RUNTIME` | `1` | Helps with Easy Anti-Cheat compatibility environment. |
| `__GL_SHADER_DISK_CACHE_SKIP_CLEANUP` | `1` | *(NVIDIA Only)* Prevents the driver from aggressively deleting compiled shaders, which helps reduce loading times on subsequent launches. |

### 3. Other Settings
*   **GameMode:** Enable "Use GameMode" (check the box). This automatically handles system limits and priorities.
*   **Wine Version:** Use the latest **GE-Proton** (e.g., GE-Proton9-20 or newer).

## Verified System Spec
The fix was confirmed working on the following configuration:

*   **OS:** Fedora Linux 42 (Workstation Edition) - Flatpak Runtime
*   **CPU:** 12th Gen Intel(R) Core(TM) i5-12400F (12 Threads)
*   **GPU:** NVIDIA GeForce RTX 3060 Ti LHR
*   **RAM:** 16 GB
*   **Driver:** NVIDIA Proprietary
*   **Launcher:** Heroic Games Launcher 2.18.1 "Waterfall Beard"
