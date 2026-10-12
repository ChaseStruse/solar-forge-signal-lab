from copy import deepcopy
from PySide6.QtCore import QCoreApplication, QObject, Signal
from solar_forge_signal_lab.controller import StudioController

APP = QCoreApplication.instance() or QCoreApplication([])


class FakeEngine(QObject):
    changed = Signal()
    failed = Signal(str)
    def __init__(self):
        super().__init__()
        self.playing = False
        self.mixer = None
    def update_mix(self, levels, muted, master):
        self.state = deepcopy((levels, muted, master))
    def play(self):
        self.playing = True
        self.changed.emit()
    def pause(self):
        self.playing = False
        self.changed.emit()
    def close(self):
        self.pause()


def test_start_silent_dirty_cancel_discard(tmp_path):
    c = StudioController(tmp_path, FakeEngine())
    assert not c.playing
    c.setLevel(0, .91)
    c.requestPreset(1)
    c.resolveSwitch('cancel')
    assert c.levels[0] == .91 and c.presetIndex == 0
    c.requestPreset(1)
    c.resolveSwitch('discard')
    assert c.presetIndex == 1 and not c.dirty
    c.close()
    assert not StudioController(tmp_path, FakeEngine()).playing


def test_save_switch_destination_survives_reorder(tmp_path):
    c = StudioController(tmp_path, FakeEngine())
    assert c.savePreset('A', True)
    assert c.savePreset('B', True)
    c.requestPreset(3)
    c.setLevel(0, .88)
    c.requestPreset(4)
    assert c.savePreset('A renamed', False)
    assert c.presetName == 'B'
    assert next(p for p in c.store.custom if p['name'] == 'A renamed')['levels'][0] == .88


def test_failed_save_does_not_switch_or_clear_dirty(tmp_path):
    c = StudioController(tmp_path, FakeEngine())
    c.setMaster(.2)
    c.requestPreset(1)
    c.store.read_only = True
    c.store.error = 'File preserved'
    assert not c.savePreset('Mine', True)
    assert c.dirty and c.presetIndex == 0
    assert c.pending_index == 1


def test_rename_delete_and_duplicate_names(tmp_path):
    c = StudioController(tmp_path, FakeEngine())
    assert not c.savePreset('Deep Space', True)
    assert c.savePreset('Custom', True)
    assert c.savePreset('Renamed', False)
    assert len(c.store.custom) == 1
    assert c.deletePreset()
    assert not c.store.custom and c.presetIndex == 0


def test_restored_unsaved_mix_stays_dirty(tmp_path):
    c = StudioController(tmp_path, FakeEngine())
    c.setLevel(0, .99)
    c.close()
    restored = StudioController(tmp_path, FakeEngine())
    assert restored.levels[0] == .99
    assert restored.dirty and not restored.playing
