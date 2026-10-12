import QtQuick

Item {
    id: scene
    objectName: "cockpitScene"
    property bool animate: false
    property real reactor: .65
    property real rain: .25
    property real radio: .12
    property real phase: 0
    clip: true
    onReactorChanged: frame.requestPaint()
    onRainChanged: weather.requestPaint()
    onRadioChanged: frame.requestPaint()
    Timer {
        interval: 40; running: scene.animate; repeat: true
        onTriggered: { scene.phase += .04; weather.requestPaint() }
    }

    Rectangle { anchors.fill: parent; color: "#000000" }

    // White points emerge slowly from the flight horizon. Nearby stars move
    // faster; each has a deterministic, independent twinkle instead of flicker.
    Repeater {
        model: 155
        delegate: Item {
            required property int index
            readonly property real seed: ((index * 73.137) % 157) / 157
            readonly property real depth: (seed + scene.phase * (.008 + (index % 4) * .0015)) % 1
            readonly property real perspective: .24 + 2.8 * depth * depth
            readonly property real angle: index * 2.399963
            readonly property real spread: .25 + ((index * 19.37) % 100) / 135
            readonly property real shimmer: .62 + .38 * Math.sin(scene.phase * (1.1 + index % 7 * .19) + index * 1.73)
            x: scene.width * .47 + Math.cos(angle) * scene.width * .52 * spread * perspective
            y: scene.height * .43 + Math.sin(angle) * scene.height * .66 * spread * perspective
            opacity: Math.min(1, depth * 12) * Math.min(1, (1 - depth) * 12) * shimmer
            Rectangle {
                anchors.centerIn: parent
                width: .8 + parent.depth * 1.6; height: width; radius: width / 2
                color: "white"
            }
            Rectangle {
                visible: index % 17 === 0
                anchors.centerIn: parent
                width: 8; height: 1; color: "white"; opacity: .4
            }
            Rectangle {
                visible: index % 17 === 0
                anchors.centerIn: parent
                width: 1; height: 8; color: "white"; opacity: .4
            }
        }
    }

    // Planet textures are painted once, then moved as scene-graph items.
    // Wraps and palette changes occur completely beyond the viewport.
    Repeater {
        model: 2
        delegate: Planet {
            required property int index
            readonly property real travel: (scene.phase / 85 + index * .5 + .24) % 1
            variant: (Math.floor(scene.phase / 85 + index * .5 + .24) + index) % 3
            width: scene.height * (index === 0 ? .94 : .56)
            height: width
            x: (1 - travel) * (scene.width + width * 2.8) - width * 1.7
            y: scene.height * (index === 0 ? .2 : .06) - height * .12
            scale: .72 + travel * .45
        }
    }

    Canvas {
        id: weather
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            const c = getContext("2d"); c.reset();
            c.clearRect(0, 0, width, height);
            c.lineWidth = 1;
            for (let j = 0; j < Math.floor(scene.rain * 90); j++) {
                const rx = ((j * 93.73) % 1000) / 1000 * width;
                const ry = ((j * 53.1 + scene.phase * 85) % 600) / 600 * height * .82;
                c.strokeStyle = "rgba(141,201,211," + (.08 + (j % 4) * .035) + ")";
                c.beginPath(); c.moveTo(rx, ry); c.lineTo(rx - 5, ry + 12 + j % 17); c.stroke();
            }
        }
    }
    Canvas {
        id: frame
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            const c = getContext("2d"); const w = width; const h = height;
            c.reset(); c.clearRect(0, 0, w, h);
            // Cockpit sill and structural struts.
            c.fillStyle="#09141e";
            c.beginPath(); c.moveTo(0,h); c.lineTo(0,h*.83); c.lineTo(w*.2,h*.92); c.lineTo(w*.8,h*.92); c.lineTo(w,h*.83); c.lineTo(w,h); c.closePath(); c.fill();
            c.strokeStyle="#304b57"; c.lineWidth=2;
            c.beginPath(); c.moveTo(0,h*.83); c.lineTo(w*.2,h*.92); c.lineTo(w*.8,h*.92); c.lineTo(w,h*.83); c.stroke();
            c.strokeStyle="#0b1823"; c.lineWidth=14;
            c.beginPath(); c.moveTo(w*.12,0); c.lineTo(0,h*.8); c.moveTo(w*.88,0); c.lineTo(w,h*.8); c.stroke();
            c.strokeStyle="#2a424f"; c.lineWidth=1;
            c.beginPath(); c.moveTo(w*.12+8,0); c.lineTo(8,h*.8); c.moveTo(w*.88-8,0); c.lineTo(w-8,h*.8); c.stroke();
            const glow=.15+scene.reactor*.6;
            c.fillStyle="rgba(239,172,94,"+glow+")";
            c.fillRect(w*.3,h*.955,w*.4,2);
            c.fillStyle="#557784";
            for(let k=0;k<8;k++) c.fillRect(w*.08+k*9,h*.94,4,3);
            c.fillStyle="rgba(121,220,199,"+(.2+scene.radio*.7)+")";
            for(let k=0;k<7;k++) c.fillRect(w*.84+k*5,h*.945-(k%3)*2,2,3+k%3*2);
        }
    }
    Column {
        x: 28; y: 24; spacing: 7
        Text { text: "EXTERIOR / OBSERVATION DECK"; color: "#87adb9"; font.pixelSize: 10; font.letterSpacing: 2 }
        Text { text: "Somewhere, far from the noise."; color: "#c2d7dc"; font.pixelSize: 17; font.weight: Font.Light }
    }
    Row {
        anchors.right: parent.right; anchors.rightMargin: 26
        anchors.top: parent.top; anchors.topMargin: 24; spacing: 8
        Rectangle { width: 5; height: 5; radius: 3; color: "#90d5c3"; anchors.verticalCenter: parent.verticalCenter }
        Text { text: "DEEP SPACE  /  CRUISE"; color: "#85a8b5"; font.pixelSize: 10; font.letterSpacing: 1 }
    }
    Column {
        anchors.left: parent.left; anchors.leftMargin: 28
        anchors.bottom: parent.bottom; anchors.bottomMargin: 45; spacing: 5
        Text { text: "DRIFTING BETWEEN WORLDS"; color: "#88a6b3"; font.pixelSize: 9; font.letterSpacing: 2 }
        Text { text: "Just stay a while."; color: "#d5e3e5"; font.pixelSize: 24; font.weight: Font.Light }
    }
}
