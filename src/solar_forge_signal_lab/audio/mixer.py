"""Deterministic loop synthesis and bounded block mixing, independent of Qt."""
import numpy as np

LAYER_IDS = ("reactor", "rain", "radio")


def make_loops(rate=48000, seconds=12):
    """Periodic spectra avoid discontinuities at the loop boundary."""
    n = int(rate * seconds)
    rng = np.random.default_rng(70421)
    t = np.arange(n) / rate
    frequencies = np.fft.rfftfreq(n, 1 / rate)

    def noise(low, high):
        spectrum = rng.normal(size=(len(frequencies), 2)) + 1j * rng.normal(size=(len(frequencies), 2))
        f = frequencies[:, None]
        envelope = np.minimum(f / low, 1) ** 2 / (1 + (f / high) ** 4)
        envelope[0] = 0
        signal = np.fft.irfft(spectrum * envelope, n=n, axis=0)
        return signal / max(float(np.max(np.abs(signal))), 1e-9)

    reactor = (np.sin(2 * np.pi * 55 * t) * .48 + np.sin(2 * np.pi * 110 * t) * .16)
    reactor *= .85 + .15 * np.sin(2 * np.pi * t / seconds)
    reactor = np.column_stack((reactor, np.roll(reactor, 13))) + noise(25, 250) * .18
    rain = noise(350, 6500) * (.8 + .2 * np.sin(2 * np.pi * t / seconds))[:, None]
    radio = noise(700, 2600) * (.35 + .25 * np.sin(2 * np.pi * t * 3 / seconds))[:, None]
    return [np.asarray(x / max(1, float(np.max(np.abs(x)))), dtype=np.float32)
            for x in (reactor, rain, radio)]


class Mixer:
    def __init__(self, loops, rate=48000):
        self.loops = loops
        self.rate = rate
        self.positions = [0] * len(loops)
        self.targets = np.zeros(len(loops), dtype=np.float32)
        self.current = self.targets.copy()
        self.ramp_frames = max(1, int(rate * .04))
        self.peak = 0.0
        self.rms = 0.0

    def set_mix(self, levels, muted, master):
        # Each normalized layer contributes at most 0.28: three layers <= 0.84.
        self.targets = np.array([min(1, max(0, v)) * (not m) * min(1, max(0, master)) * .28
                                 for v, m in zip(levels, muted)], dtype=np.float32)

    def fade_in(self):
        self.current[:] = 0

    def render(self, frames):
        out = np.zeros((frames, 2), dtype=np.float32)
        if not frames:
            return out
        ramp = np.minimum(np.arange(1, frames + 1) / self.ramp_frames, 1)
        for i, loop in enumerate(self.loops):
            indices = (np.arange(frames) + self.positions[i]) % len(loop)
            gains = self.current[i] + (self.targets[i] - self.current[i]) * ramp
            out += loop[indices] * gains[:, None]
            self.current[i] = gains[-1]
            self.positions[i] = (self.positions[i] + frames) % len(loop)
        np.clip(out, -.95, .95, out=out)
        self.peak = float(np.max(np.abs(out)))
        self.rms = float(np.sqrt(np.mean(out * out)))
        return out
