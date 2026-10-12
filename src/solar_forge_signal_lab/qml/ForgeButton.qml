import QtQuick
import QtQuick.Controls

Button {
    id: control
    property color accent: "#8ea8b5"
    property bool primary: false
    implicitHeight: 38
    implicitWidth: Math.max(80, label.implicitWidth + 28)
    hoverEnabled: true
    contentItem: Text {
        id: label
        text: control.text
        color: control.enabled ? (control.primary ? "#08161a" : control.accent) : "#475762"
        font.family: "DejaVu Sans"
        font.pixelSize: 12
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: 7
        color: control.primary ? control.accent : (control.down ? "#263b48" : control.hovered ? "#1b303d" : "#12222d")
        border.width: control.activeFocus ? 2 : 1
        border.color: control.activeFocus ? "#d1f5e9" : control.primary ? control.accent : "#2b424f"
        opacity: control.enabled ? 1 : .5
    }
}
