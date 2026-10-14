# Solar Forge Signal Lab

A native, offline spaceship soundscape studio. Mix a warm reactor hum, cockpit
rain, distant radio static, and mellow space jazz while cruising past softly lit planets. White stars
twinkle and stream outward through a truly black void, with depth-based motion.

Built with **Python 3.15.0**, PySide6/Qt Quick 6.12, and NumPy. Development is on
`Init`. The standalone app is the first release; the optional Omarchy bar companion
remains a future milestone.

## Run with Docker on Omarchy / Linux Wayland

Docker Engine and Docker Compose must already be available. Launch from an active
Wayland desktop with PipeWire's PulseAudio-compatible service (or PulseAudio).
Python, Qt, NumPy, and system libraries are installed **inside the image**, not on
the host.

```bash
./scripts/run.sh
```

This builds and starts the studio in the background. Alternatively, with the default
UID/GID of 1000:

```bash
docker compose up --build -d
```

Playback starts paused. Press **Play**, or **Ctrl+Space**, to listen. Adjust each
layer and the master volume. ON/OFF mutes a layer without losing its level.
Closing the window exits the app and stops sound; rerun the launcher to reopen it.

While playing, choose a **15, 30, or 60 minute sleep timer**. Playback fades gently
during the final 30 seconds, then pauses. Choose another duration to restart the
countdown, or **Cancel timer** to keep listening. Pausing or losing the audio output
cancels the timer. Your mix and saved volume stay unchanged; timers do not persist
across app restarts.

```bash
docker compose logs --tail=80 studio
docker compose down
```

The container runs as an unprivileged user with no network, all capabilities
removed, and only the Wayland/audio sockets and its data volume mounted. The default
software renderer avoids requiring host GPU drivers inside the image. No microphone
capture code exists in the app; access to the desktop's audio socket is not itself
an audio permission sandbox.

## Mixes and preferences

Choose Deep Space, Orbital Rain, Quiet Watch, or the jazz-led Midnight Drift, then make it your own. **Save mix**
(or **Ctrl+S**) saves a named custom preset. The save dialog can rename/update a
custom preset or save a new copy. Built-ins cannot be deleted or overwritten.
Changing presets with edits asks whether to save, discard, or cancel.

Levels, mute states, master volume, and reduced motion persist locally. Older three-layer
libraries migrate with jazz at zero volume; the original is kept in `presets.v1.backup.json`. The last
session is restored silently on launch. The named Docker volume
`solar-forge-signal-lab-data` holds `/data/presets.json`; ordinary container rebuilds
and `docker compose down` preserve it. **Do not use `down -v` unless you intend to
remove the stored presets.** Invalid or future-version files are preserved and
saving is disabled until the file is moved aside or repaired.

During playback, planets grow from the distance and pass the ship as stars stream
outward and twinkle, creating forward flight.
Reduced motion stops cockpit animation; minimizing the app also stops animation
while sound continues. Short windows scroll vertically so controls remain reachable.

## Desktop launcher (optional)

`packaging/solar-forge-signal-lab.desktop.in` is a launcher template. Replace
`@PROJECT_DIR@` with this checkout's absolute path and place it at
`~/.local/share/applications/solar-forge-signal-lab.desktop`. Keep the checkout at
that path. No desktop configuration is changed automatically.

## Development and tests

All checks can run inside the image:

```bash
docker compose build
docker run --rm --network none solar-forge-signal-lab:dev python -m pytest -p no:cacheprovider /app/tests -q
docker run --rm --network none solar-forge-signal-lab:dev python /app/scripts/check_ui.py
docker run --rm --network none -e QT_QPA_PLATFORM=offscreen -e QT_QUICK_BACKEND=software -e SIGNAL_LAB_DATA_DIR=/tmp/signal-test solar-forge-signal-lab:dev python -m solar_forge_signal_lab --smoke-test
```

For local development with an existing Python 3.15 environment, install
`requirements.lock`, install FluidSynth and the TimGM6mb SoundFont, render the music
with `python scripts/render_jazz.py`, and install the project (`pip install --no-deps -e .`), then run
`python -m solar_forge_signal_lab`. Docker is the recommended route on this machine.
The lockfile pins the tested Python dependencies; Debian security packages can
advance on a fresh build. Qt packages include upstream components the app does not
use, including WebEngine; the interface itself is native QML, with no webview.

Audio uses a single QAudioSink with a 120 ms requested output buffer and 10 ms
refill timer. Its three procedural ambience loops each contribute at most 0.18, and the bundled
jazz loop contributes at most 0.40, reserving output headroom. The original 16-bar,
76 BPM jazz arrangement is rendered during the Docker build with FluidSynth and
TimGM6mb. Loops are loaded before playback; no file reads or decoding occur during output. The UI reports output failures and
pauses after device changes or long session delays. See [asset notes](docs/assets.md).

## Troubleshooting

- **No window:** launch from your Wayland desktop and check `WAYLAND_DISPLAY` and
  `XDG_RUNTIME_DIR`. X11/macOS/Windows display forwarding is not included.
- **No audio:** check the host output device and `${XDG_RUNTIME_DIR}/pulse/native`.
  After an output change, press Play to reconnect. Read container logs for details.
- **Docker permission denied:** use your existing Docker access setup; the project
  does not change user groups, install Docker, or start privileged containers.
- **Different host user ID:** use `scripts/run.sh`, which passes your UID and GID.
  A data volume created for another user may need its ownership adjusted explicitly.

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for the design and
[verification notes](docs/verification.md) for the tested scope and remaining checks.
