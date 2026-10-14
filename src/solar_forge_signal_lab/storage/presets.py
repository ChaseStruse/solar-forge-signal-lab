"""Strict, versioned, atomic local preset storage."""
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import tempfile
import uuid

BUILTINS = [
    dict(id="deep-space", name="Deep Space", levels=[.65, .25, .12, 0], muted=[False]*4, master=.5, reduced=False),
    dict(id="orbital-rain", name="Orbital Rain", levels=[.35, .85, .08, 0], muted=[False]*4, master=.5, reduced=False),
    dict(id="quiet-watch", name="Quiet Watch", levels=[.3, .12, .25, 0], muted=[False]*4, master=.4, reduced=False),
    dict(id="midnight-drift", name="Midnight Drift", levels=[.18, .22, .035, .9], muted=[False]*4, master=.55, reduced=False),
]


def validate_mix(raw):
    if not isinstance(raw, dict):
        raise ValueError("Preset must be an object.")
    result = {}
    for key in ("id", "name"):
        value = raw.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > 80:
            raise ValueError(f"Invalid preset {key}.")
        result[key] = value.strip()
    levels, muted = raw.get("levels"), raw.get("muted")
    if not isinstance(levels, list) or len(levels) != 4:
        raise ValueError("Preset requires four layer levels.")
    if not isinstance(muted, list) or len(muted) != 4 or any(type(v) is not bool for v in muted):
        raise ValueError("Invalid mute values.")
    for value in [*levels, raw.get("master")]:
        if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("Volumes must be finite numbers between zero and one.")
    if type(raw.get("reduced")) is not bool:
        raise ValueError("Invalid motion preference.")
    result.update(levels=list(levels), muted=list(muted), master=raw["master"], reduced=raw["reduced"])
    return result


class PresetStore:
    def __init__(self, directory):
        self.path = Path(directory) / "presets.json"
        self.custom = []
        self.last = deepcopy(BUILTINS[0])
        self.error = ""
        self.read_only = False
        self.load()

    def load(self):
        if not self.path.exists():
            return
        try:
            if self.path.stat().st_size > 1024 * 1024:
                raise ValueError("Preset file is too large.")
            raw = json.loads(self.path.read_text())
            if not isinstance(raw, dict) or type(raw.get("version")) is not int or raw["version"] not in (1, 2):
                raise ValueError("Unsupported preset file version.")
            expected_layers = ["reactor", "rain", "radio"] + (["jazz"] if raw["version"] == 2 else [])
            if raw.get("layers") != expected_layers:
                raise ValueError("Unknown layer mapping.")
            presets = raw.get("presets")
            if not isinstance(presets, list) or len(presets) > 200:
                raise ValueError("Invalid preset library.")
            def upgrade(p):
                if raw["version"] != 1:
                    return p
                if not isinstance(p, dict) or not isinstance(p.get("levels"), list) or len(p["levels"]) != 3 or not isinstance(p.get("muted"), list) or len(p["muted"]) != 3:
                    raise ValueError("Invalid legacy preset.")
                return dict(p, levels=[*p["levels"], 0], muted=[*p["muted"], False])
            custom = [validate_mix(upgrade(p)) for p in presets]
            ids = [p["id"] for p in custom] + [p["id"] for p in BUILTINS]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate preset identifiers.")
            last = validate_mix(upgrade(raw["last"]))
            if raw["version"] == 1:
                backup = self.path.with_name("presets.v1.backup.json")
                try:
                    with backup.open("xb") as stream:
                        stream.write(self.path.read_bytes())
                except FileExistsError:
                    pass
            self.custom, self.last = custom, last
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.error = f"Could not load presets: {exc} Original file preserved at {self.path}. Move it aside to enable saving."
            self.read_only = True

    def write(self, custom, last):
        if self.read_only:
            raise ValueError(self.error)
        if len(custom) > 200:
            raise ValueError("The library is limited to 200 custom presets.")
        validated = [validate_mix(p) for p in custom]
        last = validate_mix(last)
        document = dict(version=2, layers=["reactor", "rain", "radio", "jazz"], presets=validated, last=last)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=self.path.parent, prefix=".presets-", delete=False) as stream:
                temp = stream.name
                json.dump(document, stream, indent=2, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
        finally:
            if temp and os.path.exists(temp):
                os.unlink(temp)
        self.custom, self.last = deepcopy(validated), deepcopy(last)

    @staticmethod
    def new_id():
        return str(uuid.uuid4())
