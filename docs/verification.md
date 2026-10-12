# Verification — first desktop release

Environment: Linux/Omarchy Wayland desktop, Docker, Python 3.15.0, PySide6 6.12.0,
NumPy 2.5.4. Checked on 2026-10-12.

## Completed

- Container builds without installing application dependencies on the host.
- Core tests cover loop wrap, finite bounded synthesis, gain ramps, mute, headroom,
  preset round trips, malformed/future-version files, atomic-write failure, duplicate
  names, rename/delete, cancel/discard/save during switching, and silent session restore.
- Real QML interaction checks exercise Save mix, text entry, custom preset creation,
  canceling a dirty preset switch, and reaching transport in an 860×680 window.
  No QML errors were emitted during these checks.
- An offscreen 1280×870 render was visually inspected. Compact layout is checked
  with a scrolling content area.
- Real Wayland window opened from Docker. The host audio server showed the studio's
  active float32 stereo 48 kHz stream on Built-in Audio Analog Stereo.
- A two-minute playback run finished with zero reported QAudioSink underruns.
- Static scene rendering was separated from animated rain after profiling. A settled
  playback sample after the change used 6.45% CPU (Docker's one-core scale) and
  approximately 105 MiB memory. These are spot measurements, not benchmarks.

## Remaining manual validation

The 30-minute soak target from the implementation plan has not been completed.
Subjective listening quality, physical device unplug/replug, suspend/resume, and
keyboard-only coverage of every control require further manual validation. No claim
of production audio hardening or support for other desktop platforms is made.
The optional Omarchy companion is not included in this first release.

Qt may print optional PipeWire/FFmpeg backend discovery messages in the slim image.
The application uses the available low-level QAudioSink through the mounted
PulseAudio-compatible socket; the measured playback stream confirms this path works.
Some Wayland text-input focus diagnostics were also emitted during the real-window
checks, without QML load or playback failures.

## Reproduce

```bash
docker compose build
docker run --rm --network none solar-forge-signal-lab:dev python -m pytest -p no:cacheprovider /app/tests -q
docker run --rm --network none solar-forge-signal-lab:dev python /app/scripts/check_ui.py
docker compose run --rm -e SIGNAL_LAB_DATA_DIR=/tmp/signal-audio-test studio python -m solar_forge_signal_lab --audio-test-seconds 120
```

The audio command intentionally plays sound, exits automatically, and uses temporary
preset storage. It reports generated frame count, peak amplitude, and underruns;
audio failures produce a nonzero exit code. Use `--audio-test-seconds 1800` for the
longer soak. Do not run the regular studio simultaneously with the audio test.

Python release reference: [Python 3.15.0, released October 9, 2026](https://www.python.org/downloads/release/python-3150/).
