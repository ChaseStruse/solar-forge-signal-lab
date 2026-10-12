import argparse
import logging
import os
from pathlib import Path
import sys
from PySide6.QtCore import QStandardPaths, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow  # Register the window wrapper for capture.
from .controller import StudioController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true", help="Open the UI briefly, then exit")
    parser.add_argument("--audio-test-seconds", type=int, default=0)
    parser.add_argument("--screenshot", help="Write a window image after rendering")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    app = QGuiApplication(sys.argv[:1])
    app.setOrganizationName("SolarForge")
    app.setApplicationName("SignalLab")
    app.setApplicationDisplayName("Solar Forge Signal Lab")
    app.setDesktopFileName("solar-forge-signal-lab")
    directory = os.environ.get("SIGNAL_LAB_DATA_DIR") or QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    controller = StudioController(directory)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("studio", controller)
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "qml" / "Main.qml")))
    if not engine.rootObjects():
        return 1
    app.aboutToQuit.connect(controller.close)
    if args.screenshot:
        QTimer.singleShot(1600, lambda: engine.rootObjects()[0].grabWindow().save(args.screenshot))
    if args.audio_test_seconds:
        QTimer.singleShot(500, controller.togglePlay)
        QTimer.singleShot(args.audio_test_seconds * 1000, app.quit)
    elif args.smoke_test:
        QTimer.singleShot(2500, app.quit)
    result = app.exec()
    if args.audio_test_seconds:
        logging.info("Audio test finished: underruns=%s", controller.engine.underruns)
    del engine
    return result
