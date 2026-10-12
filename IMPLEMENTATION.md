# Solar Forge Signal Lab — Implementation Plan

Status: standalone first release implemented on `Init` with Docker execution.
The optional Omarchy companion remains deferred. See `docs/verification.md` for
completed checks and hardware/listening checks that remain unverified.

Implementation decisions made during the first build:
- Python 3.15.0 with PySide6 6.12.0 and NumPy 2.5.4, pinned in `requirements.lock`.
- Docker is the primary launch path at the user's request; no host Python packages
  are needed. Wayland and PulseAudio-compatible sockets connect it to the desktop.
- A bounded Qt push-mode buffer with a 10 ms refill timer replaces the proposed
  producer thread. The initial three-layer mixer is small enough for this approach;
  retain the audio soak gate before calling it production-hardened.
- Original periodic procedural audio replaces bundled recordings in this first pass.
- Static cockpit rendering is separated from animated rain to reduce software-renderer
  work. Python dependencies use a pinned pip lockfile instead of introducing uv.

The sections below retain the intended design and acceptance criteria.
Development branch: `Init`.

## Product direction

Build a native Linux desktop soundscape studio with an animated spaceship cockpit.
The user can mix reactor hum, cockpit rain, and radio static, watch the scene react,
and save a favorite atmosphere. Everything needed for the initial experience works
offline, without accounts, subscriptions, or external services.

The first satisfying moment: open Signal Lab, press Play, bring up the rain, lower
the reactor, and watch the cockpit settle into a personal deep-space atmosphere.

## Decision: desktop app first, optional Omarchy companion later

| Approach | Strength | Tradeoff |
| --- | --- | --- |
| Standalone desktop app | Dedicated space for mixing and animation; independent application lifecycle; usable outside Omarchy | Requires its own launcher and packaging |
| Omarchy-only plugin | Immediate bar access and close integration with the desktop | Couples the product to the shell runtime and plugin lifecycle |
| Desktop app with companion plugin | Full studio plus quick desktop controls | Adds an integration surface to maintain after the core works |

Recommended direction: build the standalone application, then add a small optional
Omarchy companion. Audio processing and full scene rendering belong in the app.
The companion should launch or focus it, show playback status, and offer play/pause
and master volume. A shell reload should not interrupt application playback.

This is an architectural recommendation, not a requirement to install or modify
the desktop during development. The initial release must work without the plugin.

## Proposed stack

- Python with PySide6 for application logic and native Qt integration.
- Qt Quick/QML for the cockpit, animated controls, and responsive layout.
- Qt Multimedia `QAudioSink` for one mixed PCM output stream.
- NumPy for block-based mixing if the audio prototype confirms it is useful.
- Versioned JSON for presets and settings; no database needed for the initial scope.
- `uv` for the environment and lockfile; pytest for core behavior tests.

Use standard Qt Quick components with custom styling, without a browser or webview.
Confirm compatible Python/PySide6 versions on the target Arch/Omarchy machine in
milestone 1 and pin the validated dependency set. These choices are proposed until
the audio prototype passes; do not assume Python provides hard real-time guarantees.

## First release scope

### Sound and playback

- Three bundled stereo loops: Reactor, Cockpit Rain, and Radio Static.
- Independent volume and mute per layer, plus master volume and Play/Pause.
- Smooth gain ramps to avoid clicks when controls change.
- Seamless loop boundaries and sufficient mix headroom to prevent clipping.
- A visible playback/error state and a clear recovery action if output is unavailable.
- Start paused on launch, with a conservative default master volume.

Use original or appropriately licensed audio with a recorded source and license
for every asset. Procedurally generated loops are acceptable for the prototype;
listen to them before treating them as finished sound design. Avoid intelligible
radio speech in the initial asset set.

### Cockpit and controls

- One scene: a quiet cockpit looking out into deep space.
- Reactor glow responds to reactor level; rain density responds to rain level;
  radio activity responds to static level.
- An overall meter uses the actual mixed signal amplitude. Decorative animation
  must not be presented as frequency analysis.
- Clear labels, keyboard-operable controls, visible focus, and readable contrast.
- Reduced-motion option; stop rendering animations when minimized while allowing
  audio to continue.
- Closing the window exits and stops audio in the first release. Background mode
  can be introduced deliberately with the companion integration.

### Presets and local storage

- Three built-in mixes using the same layers: Deep Space, Orbital Rain, and Quiet Watch.
- Save, rename, load, and delete custom presets; built-ins remain available.
- Store schema version, preset ID/name, stable layer IDs, gains, mute flags, master
  gain, and visual preferences. Do not embed audio in preset JSON.
- Store preferences and custom presets in platform-appropriate user directories
  through Qt standard paths, separate from the source checkout.
- Validate loaded data, reject unsupported versions with a useful message, and
  write atomically. Preserve invalid files for recovery rather than overwriting them.
- Track unsaved preset changes and offer Save, Discard, or Cancel before replacing
  an edited mix. Remember settings, but never resume sound automatically on launch.

## Interface outline

The window opens directly into the studio. A top strip contains the scene name,
preset selector, and save action. The central viewport holds the cockpit. A lower
mixer contains three labeled layer strips, followed by master volume and transport.
At narrow sizes, controls wrap or scroll without hiding playback controls.

Visual direction: dark navy panels, warm amber reactor light, cool cyan instruments,
restrained bloom, and slow star movement. Keep the scene atmospheric enough for long
sessions and the controls readable enough to use without hunting through decoration.
Build the first scene from QML shapes and particles; add raster artwork only when
the composition needs it. Exact art direction can evolve after the playable prototype.

## Architecture and audio design

Keep scene state independent of QML. A Python controller exposes typed properties
and commands; views display state and send user intent. Persistence does not run
inside views, and audio processing must not depend on the animation frame rate.

Proposed source layout:

```text
src/solar_forge_signal_lab/
  app.py                 # Application startup and shutdown
  controller.py          # UI-facing state and commands
  models.py              # Layer, mix, and preset models
  audio/
    engine.py            # Output lifecycle and device handling
    mixer.py             # Block mixing, looping, gain ramps, meters
    assets.py            # Audio loading and validation
  storage/
    presets.py           # Versioned loading and atomic writes
    settings.py          # Local preferences
  qml/
    Main.qml
    components/
    scenes/
  assets/audio/
tests/
docs/assets.md           # Asset provenance and licenses
```

Decode bundled loops once, outside the playback path, and convert them to a common
supported format. Target 48 kHz stereo float PCM when supported; query the output
device and handle format differences explicitly. Each layer has its own loop cursor.
Mix fixed-size blocks into one stream with smoothed gains and a documented headroom
policy. Bound output amplitude even at maximum user settings.

Prototype a bounded producer buffer feeding `QAudioSink` through a `QIODevice`.
Keep file access, decoding, and expensive work out of audio reads. Define thread
ownership and command transfer explicitly; never manipulate QML from an audio worker.
On starvation, return silence as appropriate and record an underrun rather than
blocking the UI. Meter updates should be throttled independently of audio delivery.

Pause must stop audible output promptly and preserve loop positions; resume ramps
in smoothly. Output-device loss should move playback to a recoverable paused/error
state. Handle suspend/resume and default-output changes without unexpected autoplay.
If this design cannot sustain playback under normal desktop load, revisit the audio
backend before adding features. Do not conceal buffering problems with visual polish.

## Implementation milestones

### 1. Establish the audio foundation

Create package metadata, a locked environment, and a minimal native test window.
Load three prototype loops and implement mixing, mute, gain ramps, master level,
and output lifecycle. Record the chosen device format, buffer strategy, and results.

Acceptance: three layers play together for 30 minutes on the target machine while
ordinary desktop work continues; log underruns and investigate audible interruptions.
Sliders and mute do not click, repeated looping has no audible seam, and maximum
settings do not clip. Device removal and application exit release resources cleanly.

### 2. Deliver the first enjoyable studio

Build the cockpit and accessible mixer, connect visuals to state and actual metering,
and add reduced motion and minimized-window behavior. Replace any unpleasant test
audio with a curated set and document its provenance.

Acceptance: the user can create a pleasing mix immediately without setup; resize,
keyboard operation, minimize/restore, and playback all work together. Profile idle,
visible playback, and minimized playback; record CPU, memory, and rendering behavior
on the target machine rather than promising unmeasured performance numbers.

### 3. Make mixes reusable

Add built-in presets, custom preset CRUD, dirty-state handling, settings persistence,
validation, and recovery messages.

Acceptance: a saved mix survives restart with all levels and mute states intact;
startup remains silent; malformed or future-version data does not destroy user files;
canceling a preset switch preserves the current mix.

### 4. Prepare a usable desktop release

Add a desktop entry and icon, documented local install/run/uninstall steps, dependency
and asset licensing information, and a short usage guide. Select the distribution
format after a clean-environment installation test; support the requested Docker audio/display forwarding path.

Acceptance: a clean supported environment can launch the app from its desktop menu,
play bundled assets offline, save a preset, and quit without an orphaned process.

### 5. Optional Omarchy companion

After the standalone experience is stable, expose a small versioned session D-Bus
interface for status, raise-window, play/pause, and master volume. Prototype and verify
the shell's available IPC integration before committing to a plugin implementation.
Enforce a single application instance so launching from the bar cannot double audio.

The plugin is a controller, not a second mixer. Show an honest unavailable state
when the app is absent; offer launch without silently installing anything. Keep its
manifest, dependencies, lifecycle, and setup documented. Re-read current Omarchy
plugin guidance before implementation and validate against the installed shell.

Acceptance: launch/focus and controls work; disabling or reloading the companion
does not stop or duplicate playback; the app remains usable without Omarchy.

## Verification strategy

- Unit-test audible-behavior risks: loop wrap, block boundaries, gain ramps, mute,
  pause/resume cursor handling, and peak bounds using deterministic sample buffers.
- Test preset round trips, unknown versions, malformed values, atomic-write failure,
  and preservation of existing user files.
- Exercise controller state transitions and output failures with a fake audio backend.
- Perform real-device listening tests; mocked tests cannot establish audio quality.
- Manually verify Wayland launch, keyboard focus, small-window layout, reduced motion,
  minimize/restore, suspend/resume, device changes, and clean shutdown.

## Deferred ideas

Custom audio imports, scheduled ship flybys, richer radio events, multiple cockpit
scenes, sleep timers, exported mixes, and Omarchy theme following are later options.
Cloud sync, AI-generated sound, a timeline editor, and third-party audio plugins are
outside the initial scope. Grow the app from a convincing listening experience.

## Reference documentation

Checked while preparing this plan on 2026-10-12; verify API details during development.

- [Qt audio overview](https://doc.qt.io/qtforpython-6/overviews/qtmultimedia-audiooverview.html)
- [PySide6 QAudioSink](https://doc.qt.io/qtforpython-6/PySide6/QtMultimedia/QAudioSink.html)
- [Omarchy shell plugins](https://omarchy.org/manual/shell-plugins/)
- [Omarchy plugin development](https://plugins.omarchy.org/develop.html)
