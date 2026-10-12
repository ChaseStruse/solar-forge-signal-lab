"""Qt push-mode output: bounded 120 ms buffer, refilled in small blocks."""
import logging
import time
import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtMultimedia import QAudio, QAudioFormat, QAudioSink, QMediaDevices
from .mixer import Mixer, make_loops

log = logging.getLogger(__name__)


class AudioEngine(QObject):
    changed = Signal()
    failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playing = False
        self.sink = None
        self.output = None
        self.mixer = None
        self.format = None
        self.pending = b""
        self.underruns = 0
        self.frames_rendered = 0
        self.max_peak = 0.0
        self.levels, self.muted, self.master = [.65, .25, .12], [False] * 3, .5
        self.devices = QMediaDevices(self)
        self.devices.audioOutputsChanged.connect(self.device_changed)
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.pump)
        self.last_pump = 0

    def prepare(self):
        device = QMediaDevices.defaultAudioOutput()
        if device.isNull():
            raise RuntimeError("No audio output found. Check your sound device and try Play again.")
        fmt = QAudioFormat()
        fmt.setSampleRate(48000)
        fmt.setChannelCount(2)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Float)
        if not device.isFormatSupported(fmt):
            fmt = device.preferredFormat()
        if fmt.channelCount() not in (1, 2) or fmt.sampleFormat() not in (
            QAudioFormat.SampleFormat.Float, QAudioFormat.SampleFormat.Int16, QAudioFormat.SampleFormat.Int32):
            raise RuntimeError("This output format is unsupported. Choose a stereo output and retry.")
        if self.mixer is None or self.mixer.rate != fmt.sampleRate():
            self.mixer = Mixer(make_loops(fmt.sampleRate()), fmt.sampleRate())
        self.format = fmt
        self.sink = QAudioSink(device, fmt, self)
        self.sink.setBufferSize(fmt.bytesForDuration(120000))
        self.sink.stateChanged.connect(self.state_changed)
        log.info("Audio output: %s, %s Hz, %s channels, %s", device.description(),
                 fmt.sampleRate(), fmt.channelCount(), fmt.sampleFormat())

    def update_mix(self, levels, muted, master):
        self.levels, self.muted, self.master = list(levels), list(muted), master
        if self.mixer:
            self.mixer.set_mix(self.levels, self.muted, self.master)

    def play(self):
        if self.playing:
            return
        try:
            if self.sink is None:
                self.prepare()
            self.update_mix(self.levels, self.muted, self.master)
            self.mixer.fade_in()
            self.pending = b""
            self.output = self.sink.start()
            if self.output is None:
                raise RuntimeError("Could not open audio output. Check the Docker audio socket and retry.")
            self.playing = True
            self.last_pump = time.monotonic()
            self.pump()
            self.timer.start()
            self.changed.emit()
        except Exception as exc:
            self.pause()
            self.release()
            self.failed.emit(str(exc))

    def pause(self):
        self.playing = False
        self.timer.stop()
        if self.sink:
            self.sink.reset()
        self.output = None
        self.pending = b""
        self.changed.emit()

    def release(self):
        if self.sink:
            self.sink.deleteLater()
            self.sink = None

    def device_changed(self):
        was_playing = self.playing
        self.pause()
        self.release()
        if was_playing:
            self.failed.emit("Audio output changed. Playback paused; press Play to reconnect.")

    def state_changed(self, state):
        if self.playing and state == QAudio.State.StoppedState and self.sink.error() != QAudio.Error.NoError:
            self.pause()
            self.release()
            self.failed.emit("Audio output disconnected. Check your device, then press Play to retry.")

    def pump(self):
        if not self.playing or self.output is None:
            return
        now = time.monotonic()
        if now - self.last_pump > 2:
            self.pause()
            self.failed.emit("Session resumed after a delay. Press Play when you are ready.")
            return
        self.last_pump = now
        if self.sink.error() == QAudio.Error.UnderrunError:
            self.underruns += 1
            log.warning("Audio underrun: %s", self.underruns)
        free = self.sink.bytesFree()
        while free >= self.format.bytesPerFrame():
            if not self.pending:
                frames = min(1024, free // self.format.bytesPerFrame())
                block = self.mixer.render(frames)
                self.frames_rendered += frames
                self.max_peak = max(self.max_peak, self.mixer.peak)
                if self.format.channelCount() == 1:
                    block = block.mean(axis=1)
                kind = self.format.sampleFormat()
                if kind == QAudioFormat.SampleFormat.Int16:
                    block = (block * 32767).astype('<i2')
                elif kind == QAudioFormat.SampleFormat.Int32:
                    block = (block.astype(np.float64) * 2147483647).astype('<i4')
                else:
                    block = block.astype('<f4')
                self.pending = block.tobytes()
            written = self.output.write(self.pending[:free])
            if written < 0:
                self.pause()
                self.release()
                self.failed.emit("Audio write failed. Press Play to reconnect.")
                return
            if written == 0:
                break
            self.pending = self.pending[written:]
            free -= written

    def close(self):
        self.pause()
        self.release()
