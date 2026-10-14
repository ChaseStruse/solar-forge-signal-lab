import QtQuick
import QtQuick.Controls

Slider {
    id: control
    property color accent: "#84d7c5"
    from: 0
    to: 1
    stepSize: .01
    implicitHeight: 34
    background: Rectangle {
        x: control.leftPadding
        y: control.topPadding + control.availableHeight / 2 - height / 2
        width: control.availableWidth
        height: 4
        radius: 2
        color: "#243946"
        Rectangle { width: control.visualPosition * parent.width; height: parent.height; radius: 2; color: control.accent }
    }
    handle: Rectangle {
        x: control.leftPadding + control.visualPosition * (control.availableWidth - width)
        y: control.topPadding + control.availableHeight / 2 - height / 2
        width: 14; height: 14; radius: 7
        color: control.pressed ? "white" : control.accent
        border.width: control.activeFocus ? 3 : 0
        border.color: "#e0faf2"
    }
}
