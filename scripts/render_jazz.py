"""Render an original 16-bar space-jazz arrangement with FluidSynth/TimGM6mb.

Build-time only: the running app reads the finished PCM loop without a synth.
"""
import ctypes as C
from ctypes.util import find_library
from pathlib import Path
import wave
import numpy as np

RATE = 48000
BPM = 76
BEAT = 60 / BPM
BARS = 16
FRAMES = round(BARS * 4 * BEAT * RATE)


def score():
    rng = np.random.default_rng(6819)
    events = []
    def note(beat, duration, channel, pitch, velocity):
        # Slight timing/velocity variation is fixed across renders.
        beat = max(0, beat + rng.uniform(-.014, .014))
        events.append((round(beat * BEAT * RATE), True, channel, pitch, int(velocity)))
        events.append((round((beat + duration) * BEAT * RATE), False, channel, pitch, 0))

    harmony = [
        (38, [53, 60, 64, 69]), (31, [53, 59, 64, 69]),
        (36, [52, 59, 62, 67]), (33, [55, 61, 64, 70]),
        (38, [53, 60, 64, 69]), (31, [53, 59, 64, 69]),
        (36, [52, 59, 62, 67]), (36, [52, 57, 62, 67]),
        (41, [57, 60, 64, 67]), (34, [56, 62, 65, 69]),
        (40, [55, 59, 62, 66]), (33, [55, 61, 64, 70]),
        (38, [53, 60, 64, 69]), (31, [53, 59, 64, 69]),
        (36, [52, 59, 62, 67]), (33, [55, 61, 64, 70]),
    ]
    # Hand-written phrases with breathing space; no quoted melody.
    phrases = {
        1: [(1.66, 74, .55), (2.66, 71, .55), (3.33, 69, .45)],
        2: [(.33, 67, 1.4), (2.66, 64, .85)],
        4: [(.66, 69, .55), (1.66, 72, .85), (3.0, 76, .55)],
        5: [(.33, 74, 1.3), (2.66, 71, .55)],
        6: [(1.0, 67, 1.6)],
        9: [(.66, 69, .55), (1.66, 65, .55), (2.66, 62, .85)],
        10: [(.33, 66, 1.2), (2.33, 67, .55), (3.0, 71, .55)],
        12: [(1.0, 69, .85), (2.33, 72, .55), (3.0, 76, .55)],
        13: [(.66, 74, .8), (2.0, 71, 1.15)],
        14: [(.66, 67, 1.6)],
    }
    for bar, (root, chord) in enumerate(harmony):
        b = bar * 4
        next_root = harmony[(bar + 1) % BARS][0]
        for offset, pitch, vel in [(0, root, 78), (1.66, root+7, 58), (2.5, root+12, 65), (3.33, next_root-1, 50)]:
            note(b+offset, .6 if offset else .95, 0, pitch, vel)
        for start, duration, velocity in [(.1, 1.6, 49), (2.66, .9, 38)]:
            for n, pitch in enumerate(chord):
                note(b+start+n*.018, duration, 1, pitch, velocity+rng.integers(-4, 5))
        for beat in range(4):
            note(b+beat, .2, 9, 51, 29 + beat%2*5)
            if beat in (1, 3):
                note(b+beat+.66, .12, 9, 42, 24)
                note(b+beat, .15, 9, 38, 22)
            if beat in (0, 2):
                note(b+beat, .18, 9, 36, 35)
        for offset, pitch, duration in phrases.get(bar, []):
            note(b+offset, duration, 2, pitch, 43+rng.integers(-4, 5))
    return sorted(events)


def render(destination):
    lib = C.CDLL(find_library('fluidsynth') or 'libfluidsynth.so.3')
    def bind(name, args, result=C.c_int):
        fn = getattr(lib, name); fn.argtypes = args; fn.restype = result; return fn
    ptr = C.c_void_p; integer = C.c_int
    settings_new = bind('new_fluid_settings', [], ptr)
    settings_del = bind('delete_fluid_settings', [ptr], None)
    setnum = bind('fluid_settings_setnum', [ptr, C.c_char_p, C.c_double])
    setint = bind('fluid_settings_setint', [ptr, C.c_char_p, integer])
    synth_new = bind('new_fluid_synth', [ptr], ptr)
    synth_del = bind('delete_fluid_synth', [ptr], None)
    sfload = bind('fluid_synth_sfload', [ptr, C.c_char_p, integer])
    program = bind('fluid_synth_program_change', [ptr, integer, integer])
    cc = bind('fluid_synth_cc', [ptr, integer, integer, integer])
    on = bind('fluid_synth_noteon', [ptr, integer, integer, integer])
    off = bind('fluid_synth_noteoff', [ptr, integer, integer])
    write = bind('fluid_synth_write_float', [ptr, integer, ptr, integer, integer, ptr, integer, integer])
    settings = settings_new()
    if not settings:
        raise RuntimeError('Could not create FluidSynth settings')
    synth = None
    try:
        setnum(settings, b'synth.sample-rate', RATE)
        setnum(settings, b'synth.gain', .65)
        setnum(settings, b'synth.reverb.room-size', .55)
        setnum(settings, b'synth.reverb.level', .2)
        setint(settings, b'synth.chorus.active', 0)
        setint(settings, b'synth.cpu-cores', 1)
        synth = synth_new(settings)
        if not synth or sfload(synth, b'/usr/share/sounds/sf2/TimGM6mb.sf2', 1) < 0:
            raise RuntimeError('TimGM6mb SoundFont could not be loaded')
        for channel, instrument, volume, pan in [(0, 32, 104, 60), (1, 4, 87, 43), (2, 66, 68, 79)]:
            program(synth, channel, instrument)
            cc(synth, channel, 7, volume); cc(synth, channel, 10, pan)
        cc(synth, 9, 7, 72)
        # Run one whole cycle before capture, preserving releases/reverb at wrap.
        events = score()
        output = np.zeros((FRAMES, 2), dtype=np.float32)
        for cycle in range(2):
            cursor = 0
            for frame, active, channel, pitch, velocity in [*events, (FRAMES, False, 0, 0, 0)]:
                frame = min(FRAMES, frame)
                count = frame-cursor
                if count > 0:
                    block = np.empty((count, 2), dtype=np.float32)
                    if write(synth, count, block.ctypes.data, 0, 2, block.ctypes.data, 1, 2) < 0:
                        raise RuntimeError('FluidSynth render failed')
                    if cycle:
                        output[cursor:frame] = block
                    cursor = frame
                if pitch:
                    on(synth, channel, pitch, velocity) if active else off(synth, channel, pitch)
        # Gentle cyclic smoothing handles tiny synth-state differences at the seam.
        seam = round(RATE*.006)
        delta = output[0] - output[-1]
        output[-seam:] += np.linspace(0, 1, seam)[:, None] * delta
        output *= .88 / max(float(np.max(np.abs(output))), 1e-9)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(destination), 'wb') as wav:
            wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(RATE)
            wav.writeframes((output*32767).astype('<i2').tobytes())
        print(f'Rendered original Midnight Drift: {FRAMES/RATE:.1f}s, {BPM} BPM → {destination}')
    finally:
        if synth:
            synth_del(synth)
        settings_del(settings)


if __name__ == '__main__':
    render(Path(__file__).resolve().parents[1] / 'src/solar_forge_signal_lab/assets/audio/midnight-drift.wav')
