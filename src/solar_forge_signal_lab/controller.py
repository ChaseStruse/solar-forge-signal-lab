from copy import deepcopy
import logging
from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer
from .audio.engine import AudioEngine
from .storage.presets import BUILTINS, PresetStore


class StudioController(QObject):
    changed = Signal()
    meterChanged = Signal()
    confirmSwitch = Signal()
    saveRequested = Signal()

    def __init__(self, directory, engine=None, parent=None):
        super().__init__(parent)
        self.store = PresetStore(directory)
        self.mix = deepcopy(self.store.last)
        self.baseline = deepcopy(next((p for p in self.all_presets() if p["id"] == self.mix["id"]), self.mix))
        self.message = self.store.error
        self.pending_index = None
        self.engine = engine if engine is not None else AudioEngine(self)
        self.engine.changed.connect(self.changed)
        self.engine.failed.connect(self.set_message)
        self.sync_audio()
        self.meter_timer = QTimer(self)
        self.meter_timer.setInterval(60)
        self.meter_timer.timeout.connect(self.meterChanged)
        self.meter_timer.start()

    def all_presets(self):
        return BUILTINS + self.store.custom

    def sync_audio(self):
        self.engine.update_mix(self.mix["levels"], self.mix["muted"], self.mix["master"])

    @Property('QVariantList', notify=changed)
    def levels(self):
        return self.mix["levels"]

    @Property('QVariantList', notify=changed)
    def muted(self):
        return self.mix["muted"]

    @Property(float, notify=changed)
    def master(self):
        return self.mix["master"]

    @Property(bool, notify=changed)
    def reduced(self):
        return self.mix["reduced"]

    @Property(bool, notify=changed)
    def playing(self):
        return self.engine.playing

    @Property(str, notify=changed)
    def presetName(self):
        return self.mix["name"]

    @Property(bool, notify=changed)
    def dirty(self):
        return self.mix != self.baseline

    @Property(bool, notify=changed)
    def custom(self):
        return any(p["id"] == self.mix["id"] for p in self.store.custom)

    @Property('QStringList', notify=changed)
    def presetNames(self):
        return [p["name"] for p in self.all_presets()]

    @Property(int, notify=changed)
    def presetIndex(self):
        return next((i for i, p in enumerate(self.all_presets()) if p["id"] == self.mix["id"]), 0)

    @Property(str, notify=changed)
    def statusMessage(self):
        return self.message

    @Property(float, notify=meterChanged)
    def meter(self):
        return min(1, self.engine.mixer.rms * 5) if self.playing and self.engine.mixer else 0

    @Slot(str)
    def set_message(self, message):
        self.message = message
        self.changed.emit()

    @Slot(int, float)
    def setLevel(self, index, value):
        if 0 <= index < len(self.mix["levels"]):
            self.mix["levels"][index] = min(1, max(0, value))
            self.sync_audio()
            self.changed.emit()

    @Slot(int)
    def toggleMute(self, index):
        if 0 <= index < len(self.mix["levels"]):
            self.mix["muted"][index] = not self.mix["muted"][index]
            self.sync_audio()
            self.changed.emit()

    @Slot(float)
    def setMaster(self, value):
        self.mix["master"] = min(1, max(0, value))
        self.sync_audio()
        self.changed.emit()

    @Slot(bool)
    def setReduced(self, value):
        self.mix["reduced"] = value
        self.changed.emit()

    @Slot()
    def togglePlay(self):
        if self.playing:
            self.engine.pause()
        else:
            self.message = self.store.error
            self.engine.play()
        self.changed.emit()

    @Slot(int)
    def requestPreset(self, index):
        if not 0 <= index < len(self.all_presets()) or index == self.presetIndex:
            return
        self.pending_index = index
        if self.dirty:
            self.confirmSwitch.emit()
        else:
            self.apply_pending()

    def apply_pending(self):
        if self.pending_index is not None:
            self.mix = deepcopy(self.all_presets()[self.pending_index])
            self.baseline = deepcopy(self.mix)
            self.pending_index = None
            self.sync_audio()
            self.changed.emit()

    @Slot(str)
    def resolveSwitch(self, action):
        if action == "discard":
            self.apply_pending()
        elif action == "save":
            self.saveRequested.emit()
        else:
            self.pending_index = None
            self.changed.emit()

    @Slot(str, bool, result=bool)
    def savePreset(self, name, copy):
        name = name.strip()
        if not name or len(name) > 80:
            self.set_message("Choose a preset name between 1 and 80 characters.")
            return False
        preset = deepcopy(self.mix)
        preset["name"] = name
        if copy or not self.custom:
            preset["id"] = self.store.new_id()
        others = [p for p in self.store.custom if p["id"] != preset["id"]]
        if any(p["name"].casefold() == name.casefold() for p in [*BUILTINS, *others]):
            self.set_message("That preset name already exists. Choose another name.")
            return False
        destination = self.all_presets()[self.pending_index]["id"] if self.pending_index is not None else None
        try:
            self.store.write([*others, preset], preset)
        except (OSError, ValueError) as exc:
            self.set_message(str(exc))
            return False
        # Preserve destination by ID because saving can reorder custom presets.
        self.mix, self.baseline = deepcopy(preset), deepcopy(preset)
        self.message = "Preset saved locally."
        if destination:
            self.pending_index = next((i for i, p in enumerate(self.all_presets()) if p["id"] == destination), None)
        self.apply_pending()
        self.changed.emit()
        return True

    @Slot(result=bool)
    def deletePreset(self):
        if not self.custom:
            return False
        remaining = [p for p in self.store.custom if p["id"] != self.mix["id"]]
        replacement = deepcopy(BUILTINS[0])
        try:
            self.store.write(remaining, replacement)
        except (OSError, ValueError) as exc:
            self.set_message(str(exc))
            return False
        self.mix, self.baseline = replacement, deepcopy(replacement)
        self.message = "Custom preset deleted."
        self.sync_audio()
        self.changed.emit()
        return True

    @Slot()
    def dismissMessage(self):
        self.message = ""
        self.changed.emit()

    def close(self):
        self.engine.close()
        try:
            self.store.write(self.store.custom, self.mix)
        except (OSError, ValueError) as exc:
            logging.warning("Could not save last session: %s", exc)
