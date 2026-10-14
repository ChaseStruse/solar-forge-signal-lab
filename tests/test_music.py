import wave
import numpy as np
import pytest
from solar_forge_signal_lab.audio.music import load_jazz
from solar_forge_signal_lab.audio.mixer import Mixer, LAYER_GAINS


def test_four_layers_reserve_headroom_and_music_mutes():
    loops = [np.ones((100, 2), dtype=np.float32)] * 4
    mixer = Mixer(loops, rate=100, gains=LAYER_GAINS)
    mixer.set_mix([1]*4, [False]*4, 1)
    block = mixer.render(100)
    assert np.max(block) <= .941
    mixer.set_mix([1]*4, [False, False, False, True], 1)
    assert mixer.render(100)[-1, 0] == pytest.approx(.54)


def test_jazz_loader_resamples_stereo_and_preserves_bounds(tmp_path):
    path = tmp_path / 'loop.wav'
    samples = np.array([[1000, -1000], [2000, -2000], [3000, -3000], [0, 0]], dtype='<i2')
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(2); out.setsampwidth(2); out.setframerate(8000)
        out.writeframes(samples.tobytes())
    decoded = load_jazz(16000, path)
    assert decoded.shape == (8, 2)
    assert np.isfinite(decoded).all()
    np.testing.assert_allclose(decoded[::2], samples.astype(float)/32768)


def test_missing_audio_reports_rebuild(tmp_path):
    with pytest.raises(RuntimeError, match='Rebuild'):
        load_jazz(path=tmp_path / 'missing.wav')
