"""Load the bundled, build-time-rendered jazz loop into the output format."""
from pathlib import Path
import wave
import numpy as np


def load_jazz(rate=48000, path=None):
    path = Path(path) if path else Path(__file__).parents[1] / 'assets/audio/midnight-drift.wav'
    if not path.is_file():
        raise RuntimeError('Space Jazz audio is missing. Rebuild the Docker image to render the soundtrack.')
    with wave.open(str(path), 'rb') as wav:
        if wav.getnchannels() != 2 or wav.getsampwidth() != 2:
            raise ValueError('Space Jazz requires stereo 16-bit PCM audio.')
        source_rate = wav.getframerate()
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float32)/32768
    if not len(samples):
        raise ValueError('Space Jazz audio is empty.')
    if source_rate != rate:
        # Cyclic interpolation preserves the seam for alternate device rates.
        positions = np.arange(round(len(samples)*rate/source_rate)) * source_rate/rate
        extended = np.vstack((samples, samples[:1]))
        samples = np.column_stack([np.interp(positions, np.arange(len(extended)), extended[:, i]) for i in range(2)]).astype(np.float32)
    return samples
