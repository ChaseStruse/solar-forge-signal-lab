from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from solar_forge_signal_lab.storage.presets import BUILTINS, PresetStore, validate_mix


def test_round_trip(tmp_path):
    store = PresetStore(tmp_path)
    preset = deepcopy(BUILTINS[1])
    preset.update(id="custom", name="My rain", muted=[True, False, True], reduced=True)
    store.write([preset], preset)
    loaded = PresetStore(tmp_path)
    assert loaded.custom == [preset]
    assert loaded.last == preset


@pytest.mark.parametrize("content", ['{', '{"version":99}', '[]'])
def test_bad_file_is_preserved(tmp_path, content):
    path = tmp_path / "presets.json"
    path.write_text(content)
    store = PresetStore(tmp_path)
    assert store.read_only
    with pytest.raises(ValueError):
        store.write([], BUILTINS[0])
    assert path.read_text() == content


@pytest.mark.parametrize("value", [float('nan'), float('inf'), -1, 2, True, '0.5'])
def test_invalid_gain(value):
    mix = deepcopy(BUILTINS[0])
    mix["master"] = value
    with pytest.raises(ValueError):
        validate_mix(mix)


def test_atomic_failure_keeps_old_file(tmp_path):
    store = PresetStore(tmp_path)
    store.write([], BUILTINS[0])
    original = store.path.read_bytes()
    with patch('os.replace', side_effect=OSError('disk unavailable')):
        with pytest.raises(OSError):
            store.write([], BUILTINS[1])
    assert store.path.read_bytes() == original
    assert store.last == BUILTINS[0]
    assert not list(tmp_path.glob('.presets-*'))
