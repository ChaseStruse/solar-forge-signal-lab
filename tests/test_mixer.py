import numpy as np
from solar_forge_signal_lab.audio.mixer import Mixer, make_loops


def test_wrap_across_multiple_loop_boundaries():
    loop = np.array([[.2, .3], [.4, .5], [.6, .7]], dtype=np.float32)
    mixer = Mixer([loop], rate=100)
    mixer.set_mix([1], [False], 1)
    mixer.current[:] = mixer.targets
    out = mixer.render(11)
    np.testing.assert_allclose(out, loop[np.arange(11) % 3] * .28)
    assert mixer.positions == [2]


def test_gain_ramp_mute_and_headroom():
    mixer = Mixer([np.ones((100, 2), dtype=np.float32)] * 3, rate=1000)
    mixer.set_mix([1]*3, [False]*3, 1)
    out = mixer.render(100)
    assert 0 < out[0, 0] < out[39, 0]
    assert np.max(out) <= .841
    mixer.set_mix([1]*3, [True]*3, 1)
    out = mixer.render(100)
    assert out[0, 0] > out[39, 0]
    assert not out[40:].any()


def test_synthesis_is_finite_bounded_and_repeatable():
    loops = make_loops(8000, 1)
    again = make_loops(8000, 1)
    for a, b in zip(loops, again):
        assert a.shape == (8000, 2)
        assert np.isfinite(a).all()
        assert np.max(np.abs(a)) <= 1
        np.testing.assert_array_equal(a, b)
        # Boundary jumps must be comparable to ordinary adjacent samples.
        assert np.max(np.abs(a[0] - a[-1])) < np.max(np.abs(np.diff(a, axis=0))) * 2


def test_fade_in_preserves_cursor():
    mixer = Mixer([np.ones((100, 2), dtype=np.float32)], rate=1000)
    mixer.set_mix([1], [False], 1)
    mixer.render(60)
    mixer.fade_in()
    assert mixer.positions == [60]
    assert mixer.render(1)[0, 0] < .01
