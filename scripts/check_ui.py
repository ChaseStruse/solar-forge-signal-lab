"""Exercise real QML controls offscreen; run in the container."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('QT_QUICK_BACKEND', 'software')
import tempfile
from pathlib import Path
from PySide6.QtCore import QPoint, QPointF, Qt, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtTest import QTest
from solar_forge_signal_lab.controller import StudioController
from PySide6.QtCore import QObject, Signal

class SilentEngine(QObject):
    changed = Signal()
    failed = Signal(str)
    playing = False
    mixer = None
    def update_mix(self, *args): pass
    def play(self):
        self.playing = True
        self.changed.emit()
    def pause(self):
        self.playing = False
        self.changed.emit()
    def close(self): self.pause()
import solar_forge_signal_lab

app = QGuiApplication([])
errors = []
def messages(kind, context, message):
    if 'qml' in message.lower() or 'ReferenceError' in message or 'TypeError' in message:
        errors.append(message)
qInstallMessageHandler(messages)
with tempfile.TemporaryDirectory() as directory:
    controller = StudioController(directory, SilentEngine())
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('studio', controller)
    engine.load(QUrl.fromLocalFile(str(Path(solar_forge_signal_lab.__file__).parent / 'qml/Main.qml')))
    assert engine.rootObjects(), errors
    window = engine.rootObjects()[0]
    QTest.qWait(300)
    def item(name):
        def find_visual(parent):
            if parent.objectName() == name:
                return parent
            for child in parent.childItems():
                found = find_visual(child)
                if found is not None:
                    return found
            return None
        found = window.findChild(QQuickItem, name)
        if found is None:
            found = find_visual(window.contentItem())
        assert found is not None, name
        return found
    def click(name):
        obj = item(name)
        point = obj.mapToScene(QPointF(obj.width()/2, obj.height()/2))
        QTest.mouseClick(window, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(int(point.x()), int(point.y())))
        QTest.qWait(100)
    click('saveMixButton')
    field = item('presetNameField')
    assert field.hasActiveFocus()
    field.setProperty('text', 'UI test atmosphere')
    click('confirmSaveButton')
    assert controller.custom and controller.presetName == 'UI test atmosphere'
    controller.setLevel(0, .8)
    controller.requestPreset(1)
    QTest.qWait(100)
    click('cancelSwitchButton')
    assert controller.presetName == 'UI test atmosphere' and controller.dirty
    # Compact windows scroll, so transport remains accessible rather than clipped.
    window.resize(860, 680)
    QTest.qWait(100)
    scroll = item('studioScroll')
    assert scroll.property('contentHeight') > window.height()
    scroll.setProperty('contentY', scroll.property('contentHeight') - window.height())
    QTest.qWait(100)
    transport = item('transportButton')
    position = transport.mapToScene(QPointF(0, 0))
    assert 0 <= position.y() < window.height() - transport.height()
    click('transportButton')
    click('sleep15Button')
    assert controller.sleepActive and 899 <= controller.sleepRemaining <= 900
    assert 'Pausing in' in item('sleepCountdown').property('text')
    click('cancelSleepButton')
    assert not controller.sleepActive and controller.playing
    window.grabWindow().save('/tmp/signal-lab-small.png')
    controller.close()
    window.close()
    del engine
assert not errors, errors
print('UI checks passed: save dialog, custom preset, cancel switch, compact scrolling, sleep timer start/cancel; no QML errors.')
