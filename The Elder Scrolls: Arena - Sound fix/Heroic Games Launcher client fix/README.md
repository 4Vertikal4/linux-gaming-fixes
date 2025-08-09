# MIDI Playback Support for Heroic Games Launcher (Flatpak)
Enable MIDI music for older games launched via Heroic by bundling TiMidity++ and the FluidR3 GM soundfont inside the Flatpak sandbox.

## Description
This change adds built‑in MIDI playback to the Heroic Games Launcher Flatpak by integrating:
- TiMidity++ 2.15.0 (built with ALSA, ALSA sequencer, PulseAudio output, and server interface)
- FluidR3 GM soundfont (FluidR3_GM.sf2)
- A lightweight wrapper that auto‑starts TiMidity++ only when a game likely uses MIDI

Goal: Restore background music in classic titles that rely on MIDI without requiring users to set up external synths or host‑side configuration.

## What’s Included
- TiMidity++ compiled with:
  - `--enable-alsa`, `--enable-alsaseq`, `--enable-audio=alsa,pulse`, `--enable-interface=server,alsaseq`
- Soundfont and config:
  - `/app/share/soundfonts/FluidR3_GM.sf2`
  - `/app/share/soundfonts/fluid3gm.cfg`
  - `/app/share/timidity/timidity.cfg` (points to the bundled soundfont; includes basic options)
- Wrapper:
  - Installs `heroic-midi-wrapper` as `/app/bin/gamemoderun` (renames original to `/app/bin/gamemoderun-original`)
- Audio stack in‑sandbox:
  - ALSA configuration and plugins (x86_64 + i386)
  - PulseAudio client libraries
- Build fix:
  - `patches/0001-timidity-fix-missing-includes.patch` to resolve missing header issues in TiMidity++ sources
- Manifest:
  - See `com.heroicgameslauncher.hgl.yml` for the full integration. This change is strictly additive and introduces a new section labeled:
    - `# --- MIDI Support (TiMidity++ with FluidR3_GM) ---`
    - No existing variables or entries in the manifest are modified.

## How It Works
- Detection:
  - Before launching, the wrapper checks the game directory (via `STEAM_COMPAT_INSTALL_PATH` when present) for:
    - MIDI assets: `.mid`, `.midi`
    - Config references: terms like `midi`, `timidity`, `mpu-401`, or `sound.*midi`
- On positive detection:
  - Starts TiMidity++ as an ALSA sequencer server inside the sandbox (`/app/bin/timidity -iA`) using the bundled soundfont
  - Launches the game via the original runner (`/app/bin/gamemoderun-original`)
  - Shuts down TiMidity++ automatically when the game exits
- Audio output:
  - TiMidity++ plays through PulseAudio within the Flatpak, so users hear MIDI music without host‑side setup

## Paths and Artifacts
- Manifest: `com.heroicgameslauncher.hgl.yml`
- Wrapper: `/app/bin/gamemoderun` (wrapper), `/app/bin/gamemoderun-original` (original)
- TiMidity++ binary: `/app/bin/timidity`
- Config: `/app/share/timidity/timidity.cfg`
- Soundfont: `/app/share/soundfonts/FluidR3_GM.sf2` (+ `fluid3gm.cfg`)
- Patch: `patches/0001-timidity-fix-missing-includes.patch`

## Usage (End Users)
- No configuration required. When launching a game that uses MIDI, TiMidity++ auto‑starts and provides music playback.
- Non‑MIDI titles are unaffected (the wrapper is effectively a no‑op).

## Testing (Reviewers/Maintainers)
1. Build and install the Flatpak with the provided manifest.
2. Launch a known MIDI‑based title (e.g., classic DOS/Windows games via Proton/Wine).
3. Expected behavior:
   - Wrapper logs indicate detection (e.g., “Found MIDI files in game directory” or “Found MIDI configuration references”).
   - TiMidity++ starts (“Auto‑starting TiMidity++…”, “TiMidity++ ready for MIDI playback”).
   - MIDI music plays during the game.
   - On exit, TiMidity++ is terminated (“Stopping TiMidity++ …”).
4. Launch a non‑MIDI title to confirm no TiMidity++ process is started.

## Troubleshooting
- No music:
  - Detection relies on `STEAM_COMPAT_INSTALL_PATH`. If it’s not set for a particular launch path, auto‑start may not trigger.
  - Confirm the title actually uses MIDI (some use CD/OGG/streamed audio instead).
- Conflicts:
  - If another MIDI synth runs in the sandbox or host, it may contend for ALSA sequencer ports.
- Logs:
  - Run Heroic from a terminal to see wrapper messages (stdout/stderr).

## Notes and Limitations
- The wrapper is conservative: it only starts TiMidity++ when a game likely needs MIDI, minimizing overhead for non‑MIDI titles.
- Customizing soundfonts or TiMidity options currently requires modifying the Flatpak (e.g., `timidity.cfg` in the manifest).
- ALSA sequencer functionality is used inside the sandbox; behavior may vary with different runtimes/permissions.

## Security and Packaging
- All content resides under `/app`; processes are started/stopped per game session.
- ALSA/Pulse client libraries are bundled to ensure playback within the sandbox.
- Build cleanup reduces image size (removal of static libs, headers, manpages).

## Future Improvements
- Optional env flags to force‑enable or disable MIDI per‑title.
- User‑overridable soundfont and configuration paths.
- More robust detection heuristics and opt‑in logging verbosity.

## Acknowledgements
- Current review on: https://github.com/flathub/com.heroicgameslauncher.hgl/pull/222
