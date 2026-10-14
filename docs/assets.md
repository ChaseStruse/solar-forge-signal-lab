# Asset provenance

The initial three sound layers are original deterministic procedural compositions
in `audio/mixer.py`, generated locally at the selected output sample rate. They use
sine waves and shaped periodic noise, with a fixed random seed. These three layers use no recordings, third-party samples, speech, downloads, or
generative services.

Reactor: 55/110 Hz oscillators with filtered mechanical noise.
Cockpit Rain: wide stereo filtered noise with slow periodic intensity changes.
Radio Static: narrow-band noise with periodic modulation.

The cockpit, stars, rain, planet, icon, and instrument graphics are original
code-drawn artwork. Qt and NumPy retain their respective upstream licenses.
These sounds are a first sound-design pass; listening feedback should guide refinement.

Space Jazz: an original 16-bar, 76 BPM arrangement in `scripts/render_jazz.py`,
rendered at build time using FluidSynth and the Debian-provided TimGM6mb SoundFont
(upright bass, electric piano, saxophone, and drums). The generated stereo PCM loop
is bundled with the app; it is not a recording of an existing song. Upstream
FluidSynth and SoundFont license notices remain in the Docker image under
`/usr/share/doc/libfluidsynth3` and `/usr/share/doc/timgm6mb-soundfont`.
