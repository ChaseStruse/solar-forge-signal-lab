import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: root
    objectName: "studioWindow"
    width: 1280; height: 870
    minimumWidth: 860; minimumHeight: 680
    visible: true
    title: "Solar Forge · Signal Lab"
    color: "#09131c"
    font.family: "DejaVu Sans"
    property int contentMinimumHeight: width < 1100 ? 1070 : 900
    property bool motion: visibility !== Window.Minimized && studio.playing && !studio.reduced

    Connections {
        target: studio
        function onConfirmSwitch() { switchDialog.open() }
        function onSaveRequested() { saveName.text = studio.custom ? studio.presetName : "My " + studio.presetName; saveCopy.checked = !studio.custom; saveDialog.open() }
    }
    Shortcut { sequence: "Ctrl+S"; onActivated: { saveName.text = studio.custom ? studio.presetName : "My " + studio.presetName; saveCopy.checked = !studio.custom; saveDialog.open() } }
    Shortcut { sequence: "Ctrl+Space"; onActivated: studio.togglePlay() }

    Flickable {
        objectName: "studioScroll"
        anchors.fill: parent
        contentWidth: width
        contentHeight: Math.max(height, root.contentMinimumHeight)
        clip: true
        ScrollBar.vertical: ScrollBar {}
    ColumnLayout {
        x: 26; y: 26; width: parent.width - 52; height: Math.max(root.height, root.contentMinimumHeight) - 52; spacing: 18
        RowLayout {
            Layout.fillWidth: true; spacing: 14
            Rectangle {
                width: 40; height: 40; radius: 12; color: "#19342f"; border.color: "#31594d"
                Text { anchors.centerIn: parent; text: "◉"; color: "#a3d8ba"; font.pixelSize: 29 }
            }
            ColumnLayout {
                spacing: 3
                Text { text: "SOLAR FORGE"; color: "#8ba49b"; font.pixelSize: 9; font.letterSpacing: 3 }
                Text { text: "Signal Lab"; color: "#e1eae7"; font.pixelSize: 23; font.weight: Font.DemiBold }
            }
            Item { Layout.fillWidth: true }
            Text { text: "YOUR OWN LITTLE FREQUENCY"; color: "#66838d"; font.pixelSize: 10; font.letterSpacing: 1.5; visible: root.width > 1050 }
            Rectangle { width: 1; height: 25; color: "#293e47"; visible: root.width > 1050 }
            Text { text: "●  LOCAL & OFFLINE"; color: "#8ab8a3"; font.pixelSize: 10; font.letterSpacing: 1 }
        }
        Rectangle { Layout.fillWidth: true; height: 1; color: "#23343e" }
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            ColumnLayout {
                spacing: 5
                Text { text: "THE LISTENING ROOM"; color: "#77919d"; font.pixelSize: 9; font.letterSpacing: 2 }
                Text { text: studio.presetName + (studio.dirty ? "  ·" : ""); color: "#e2e9e8"; font.pixelSize: 25 }
            }
            Item { Layout.fillWidth: true }
            ComboBox {
                id: presetBox; objectName: "presetPicker"
                Layout.preferredWidth: 175
                model: studio.presetNames
                currentIndex: studio.presetIndex
                onActivated: index => studio.requestPreset(index)
                contentItem: Text { text: presetBox.displayText; color: "#bbd0d4"; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter; leftPadding: 12 }
                background: Rectangle { implicitHeight: 38; radius: 7; color: "#12222d"; border.color: presetBox.activeFocus ? "#a3d8ba" : "#2b424f" }
                delegate: ItemDelegate {
                    width: presetBox.width
                    contentItem: Text { text: modelData; color: "#d5e1df"; font.pixelSize: 12 }
                    background: Rectangle { color: highlighted ? "#29434b" : "#142530" }
                    highlighted: presetBox.highlightedIndex === index
                }
                popup: Popup {
                    y: presetBox.height + 4; width: presetBox.width; padding: 1
                    implicitHeight: Math.min(contentItem.implicitHeight + 2, 250)
                    contentItem: ListView { clip: true; implicitHeight: contentHeight; model: presetBox.popup.visible ? presetBox.delegateModel : null; currentIndex: presetBox.highlightedIndex; ScrollIndicator.vertical: ScrollIndicator {} }
                    background: Rectangle { color: "#142530"; border.color: "#385461"; radius: 5 }
                }
            }
            ForgeButton { objectName: "saveMixButton"; text: "Save mix"; accent: "#9dd5bd"; onClicked: { saveName.text = studio.custom ? studio.presetName : "My " + studio.presetName; saveCopy.checked = !studio.custom; saveDialog.open() } }
            ForgeButton { text: "Delete"; visible: studio.custom; onClicked: deleteDialog.open() }
        }
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 195
            color: "#10202b"; radius: 12; border.color: "#2b424f"
            Cockpit {
                anchors.fill: parent; anchors.margins: 1
                animate: root.motion
                reactor: studio.muted[0] ? 0 : studio.levels[0]
                rain: studio.muted[1] ? 0 : studio.levels[1]
                radio: studio.muted[2] ? 0 : studio.levels[2]
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Text { text: "BUILD YOUR ATMOSPHERE"; color: "#89a0a8"; font.pixelSize: 10; font.letterSpacing: 2 }
            Item { Layout.fillWidth: true }
            Text { text: "A little jazz. A long way from home."; color: "#64808d"; font.pixelSize: 11 }
        }
        GridLayout {
            Layout.fillWidth: true; columns: root.width < 1100 ? 2 : 4; columnSpacing: 12; rowSpacing: 12
            Repeater {
                model: [ {name: "Reactor", tag: "01 / ENGINE ROOM", detail: "A warm mechanical heartbeat", accent: "#e5b77c", glyph: "◎"},
                         {name: "Cockpit Rain", tag: "02 / OUTSIDE THE GLASS", detail: "Soft weather, distant worlds", accent: "#7cc7db", glyph: "⋮"},
                         {name: "Radio Static", tag: "03 / DEEP SPACE COMMS", detail: "A whisper from the unknown", accent: "#b8a3dc", glyph: "≋"},
                         {name: "Space Jazz", tag: "04 / MIDNIGHT DRIFT", detail: "Upright bass, warm keys, soft sax", accent: "#d8b591", glyph: "♫"} ]
                delegate: Rectangle {
                    required property var modelData
                    required property int index
                    Layout.fillWidth: true; Layout.preferredHeight: 158
                    radius: 10; color: "#111f2a"; border.color: "#243946"
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 16; spacing: 8
                        RowLayout {
                            Text { text: modelData.tag; color: "#708c99"; font.pixelSize: 8; font.letterSpacing: 1 }
                            Item { Layout.fillWidth: true }
                            Text { text: modelData.glyph; color: modelData.accent; font.pixelSize: 19 }
                        }
                        Text { text: modelData.name; color: "#dfE7e6"; font.pixelSize: 18 }
                        Text { text: modelData.detail; color: "#7b95a2"; font.pixelSize: 10; visible: root.width > 940 }
                        RowLayout {
                            Layout.fillWidth: true; spacing: 10
                            ForgeSlider { Layout.fillWidth: true; accent: modelData.accent; value: studio.levels[index]; onMoved: studio.setLevel(index, value); Accessible.name: modelData.name + " volume" }
                            Text { text: Math.round(studio.levels[index]*100).toString().padStart(2,"0"); color: modelData.accent; font.pixelSize: 12; Layout.preferredWidth: 26 }
                            ForgeButton { text: studio.muted[index] ? "OFF" : "ON"; implicitWidth: 47; implicitHeight: 29; accent: studio.muted[index] ? "#647985" : modelData.accent; onClicked: studio.toggleMute(index); Accessible.name: "Toggle " + modelData.name }
                        }
                    }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 72; radius: 10; color: "#12262c"; border.color: "#29434a"
            RowLayout {
                anchors.fill: parent; anchors.margins: 16; spacing: 16
                ForgeButton { objectName: "transportButton"; text: studio.playing ? "Ⅱ  Pause" : "▶  Play"; primary: true; accent: "#a3d8ba"; implicitWidth: 112; onClicked: studio.togglePlay(); Accessible.name: studio.playing ? "Pause playback" : "Start playback" }
                ColumnLayout {
                    spacing: 4
                    Text { text: studio.playing ? "TRANSMITTING" : "READY WHEN YOU ARE"; color: "#a5c4bc"; font.pixelSize: 9; font.letterSpacing: 1 }
                    Text { text: studio.playing ? "Your atmosphere is live" : "Press play. Find your quiet."; color: "#779a99"; font.pixelSize: 10 }
                }
                Item { Layout.fillWidth: true }
                Row {
                    spacing: 3; visible: root.width > 1020
                    Repeater {
                        model: 20
                        Rectangle { required property int index; width: 3; height: 18; radius: 1; color: index/20 < studio.meter ? "#91d7b3" : "#294641" }
                    }
                }
                Text { text: "MASTER"; color: "#87a7a6"; font.pixelSize: 9; font.letterSpacing: 1 }
                ForgeSlider { Layout.preferredWidth: 125; value: studio.master; onMoved: studio.setMaster(value); Accessible.name: "Master volume" }
                Text { text: Math.round(studio.master*100)+"%"; color: "#acd2c7"; font.pixelSize: 11; Layout.preferredWidth: 32 }
            }
        }
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Text { text: "SLEEP TIMER"; color: "#87a7a6"; font.pixelSize: 9; font.letterSpacing: 1 }
            Repeater {
                model: [15, 30, 60]
                ForgeButton {
                    required property int modelData
                    objectName: "sleep" + modelData + "Button"
                    text: modelData + " min"; enabled: studio.playing
                    onClicked: studio.startSleep(modelData)
                    Accessible.name: "Sleep in " + modelData + " minutes"
                }
            }
            Text {
                objectName: "sleepCountdown"
                text: studio.sleepActive
                    ? (studio.sleepRemaining <= 30 ? "Fading out · " : "Pausing in ")
                      + Math.floor(studio.sleepRemaining / 60) + ":"
                      + (studio.sleepRemaining % 60).toString().padStart(2, "0")
                    : "A gentle fade into quiet"
                color: "#a5c4bc"; font.pixelSize: 11
                Accessible.name: text
            }
            Item { Layout.fillWidth: true }
            ForgeButton {
                objectName: "cancelSleepButton"; text: "Cancel timer"
                visible: studio.sleepActive; onClicked: studio.cancelSleep()
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Text { text: "SIGNAL LAB  /  VOL. 001"; color: "#56717f"; font.pixelSize: 9; font.letterSpacing: 1.5 }
            Item { Layout.fillWidth: true }
            CheckBox {
                text: "Reduced motion"; checked: studio.reduced; onToggled: studio.setReduced(checked)
                contentItem: Text { text: parent.text; color: "#819aa4"; font.pixelSize: 10; leftPadding: 26; verticalAlignment: Text.AlignVCenter }
                indicator: Rectangle { x: 0; y: (parent.height-height)/2; width: 15; height: 15; radius: 3; color: studio.reduced ? "#8fc9b4" : "#172b36"; border.color: parent.activeFocus ? "#d5eee4" : "#3b5964"; Text { anchors.centerIn: parent; text: studio.reduced ? "✓" : ""; color: "#10252a"; font.pixelSize: 11 } }
            }
            Text { text: "CTRL + SPACE  PLAY / PAUSE"; color: "#56717f"; font.pixelSize: 9; visible: root.width > 1000 }
        }
        Rectangle {
            visible: studio.statusMessage.length > 0
            Layout.fillWidth: true; implicitHeight: notice.implicitHeight + 22
            radius: 6; color: "#2a2b24"; border.color: "#67593a"
            Text { id: notice; anchors.left: parent.left; anchors.right: dismiss.left; anchors.margins: 10; anchors.verticalCenter: parent.verticalCenter; text: studio.statusMessage; color: "#dfc99c"; font.pixelSize: 11; wrapMode: Text.Wrap }
            ForgeButton { id: dismiss; anchors.right: parent.right; anchors.rightMargin: 7; anchors.verticalCenter: parent.verticalCenter; text: "Dismiss"; onClicked: studio.dismissMessage(); implicitHeight: 28 }
        }
    }
    }
    Dialog {
        id: switchDialog; objectName: "switchDialog"; anchors.centerIn: parent; modal: true; title: "Keep your changes?"; width: 410
        closePolicy: Popup.NoAutoClose
        header: Text { text: parent.title; color: "#e0eae5"; font.pixelSize: 17; padding: 18 }
        background: Rectangle { color: "#192c37"; border.color: "#45616d"; radius: 10 }
        contentItem: ColumnLayout {
            Text { text: "Save your current mix before changing presets?"; color: "#d4e0e1"; wrapMode: Text.Wrap; Layout.fillWidth: true }
            RowLayout {
                ForgeButton { text: "Save…"; onClicked: { switchDialog.close(); studio.resolveSwitch("save") } }
                ForgeButton { text: "Discard"; onClicked: { switchDialog.close(); studio.resolveSwitch("discard") } }
                ForgeButton { objectName: "cancelSwitchButton"; text: "Cancel"; onClicked: { switchDialog.close(); studio.resolveSwitch("cancel") } }
            }
        }
    }
    Dialog {
        id: saveDialog; objectName: "saveDialog"; anchors.centerIn: parent; modal: true; title: studio.custom ? "Save or rename your mix" : "Save your mix"; width: 410
        closePolicy: Popup.NoAutoClose
        header: Text { text: parent.title; color: "#e0eae5"; font.pixelSize: 17; padding: 18 }
        background: Rectangle { color: "#192c37"; border.color: "#45616d"; radius: 10 }
        onOpened: { saveName.forceActiveFocus(); saveName.selectAll() }
        contentItem: ColumnLayout {
            spacing: 12
            TextField { id: saveName; objectName: "presetNameField"; Layout.fillWidth: true; maximumLength: 80; placeholderText: "Give this atmosphere a name"; color: "#e4eeea"; background: Rectangle { color: "#0d1d27"; radius: 5; border.color: "#678c8b" } Accessible.name: "Preset name" }
            CheckBox { id: saveCopy; text: "Save as a new preset"; enabled: studio.custom; contentItem: Text { text: parent.text; color: "#b2c6c9"; leftPadding: 30; verticalAlignment: Text.AlignVCenter } }
            Text { text: studio.statusMessage; visible: text.length > 0; color: "#d5bd92"; wrapMode: Text.Wrap; Layout.fillWidth: true; font.pixelSize: 11 }
            RowLayout {
                ForgeButton { objectName: "confirmSaveButton"; text: "Save"; primary: true; accent: "#a3d8ba"; onClicked: { if (studio.savePreset(saveName.text, saveCopy.checked)) saveDialog.close() } }
                ForgeButton { text: "Cancel"; onClicked: { saveDialog.close(); studio.resolveSwitch("cancel") } }
            }
        }
    }
    Dialog {
        id: deleteDialog; anchors.centerIn: parent; modal: true; title: "Delete this custom preset?"; width: 390
        header: Text { text: parent.title; color: "#e0eae5"; font.pixelSize: 17; padding: 18 }
        background: Rectangle { color: "#192c37"; border.color: "#45616d"; radius: 10 }
        contentItem: ColumnLayout {
            Text { text: studio.presetName; color: "#d4e0e1" }
            RowLayout {
                ForgeButton { text: "Delete"; accent: "#e2a68f"; onClicked: { if (studio.deletePreset()) deleteDialog.close() } }
                ForgeButton { text: "Cancel"; onClicked: deleteDialog.close() }
            }
        }
    }
}
