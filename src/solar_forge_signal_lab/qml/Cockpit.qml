import QtQuick

Item {
    id: scene
    property bool animate: false
    property real reactor: .65
    property real rain: .25
    property real radio: .12
    property real phase: 0
    clip: true
    onReactorChanged: canvas.requestPaint()
    onRainChanged: canvas.requestPaint()
    onRadioChanged: canvas.requestPaint()
    Timer {
        interval: 50; running: scene.animate; repeat: true
        onTriggered: { scene.phase += .05; canvas.requestPaint() }
    }
    Canvas {
        id: canvas
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            const c = getContext("2d"); const w = width; const h = height;
            c.reset();
            let bg = c.createLinearGradient(0, 0, w, h);
            bg.addColorStop(0, "#040d1d"); bg.addColorStop(.55, "#102b3e"); bg.addColorStop(1, "#071320");
            c.fillStyle = bg; c.fillRect(0,0,w,h);
            // Deterministic stars: no random flicker between frames.
            for (let i=0;i<150;i++) {
                let x = ((i*137.507 + scene.phase*(i%3+.3)) % 1000)/1000*w;
                let y = ((i*71.17)%600)/600*h;
                c.fillStyle = i%8===0 ? "#b5d9e2" : "#597a93";
                const r = i%8===0 ? 1.5 : .7;
                c.fillRect(x,y,r,r);
            }
            // A softly lit world beyond the glass.
            const px=w*.70, py=h*.79, pr=h*.58;
            let halo=c.createRadialGradient(px,py,pr*.85,px,py,pr*1.16);
            halo.addColorStop(0,"#487d8b"); halo.addColorStop(.78,"#173e52"); halo.addColorStop(1,"#10283b");
            c.fillStyle=halo; c.beginPath(); c.arc(px,py,pr*1.16,0,Math.PI*2); c.fill();
            let planet=c.createLinearGradient(px-pr,py-pr,px+pr,py+pr);
            planet.addColorStop(0,"#53818a"); planet.addColorStop(.25,"#224854"); planet.addColorStop(.7,"#102736"); planet.addColorStop(1,"#071320");
            c.fillStyle=planet; c.beginPath(); c.arc(px,py,pr,0,Math.PI*2); c.fill();
            c.save(); c.beginPath(); c.arc(px,py,pr,0,Math.PI*2); c.clip();
            c.strokeStyle="#476d73"; c.lineWidth=1; c.globalAlpha=.25;
            for(let k=0;k<13;k++) { c.beginPath(); c.ellipse(px,py-pr+k*pr*.18,pr*1.1,pr*.13,-.24,0,Math.PI*2); c.stroke(); }
            c.restore();
            // Rain streaks on cockpit glass, tied to the rain channel.
            c.lineWidth=1;
            for(let j=0;j<Math.floor(scene.rain*90);j++) {
                let rx=((j*93.73)%1000)/1000*w;
                let ry=((j*53.1 + scene.phase*85)%600)/600*h;
                c.strokeStyle="rgba(141,201,211,"+(.08+(j%4)*.035)+")";
                c.beginPath(); c.moveTo(rx,ry); c.lineTo(rx-5,ry+12+j%17); c.stroke();
            }
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
        Text { text: "KEPLER SECTOR  /  07"; color: "#85a8b5"; font.pixelSize: 10; font.letterSpacing: 1 }
    }
    Column {
        anchors.left: parent.left; anchors.leftMargin: 28
        anchors.bottom: parent.bottom; anchors.bottomMargin: 45; spacing: 5
        Text { text: "NO DESTINATION REQUIRED"; color: "#88a6b3"; font.pixelSize: 9; font.letterSpacing: 2 }
        Text { text: "Just stay a while."; color: "#d5e3e5"; font.pixelSize: 24; font.weight: Font.Light }
    }
}
