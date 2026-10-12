import QtQuick

Canvas {
    id: planet
    property int variant: 0
    onVariantChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onPaint: {
        const c = getContext("2d");
        c.reset(); c.clearRect(0, 0, width, height);
        const x = width * .5, y = height * .5, r = width * .37;
        const palettes = [
            ["#b4dfed", "#467f99", "#1b405a", "#030911", "#91c9d9"],
            ["#eed9b2", "#b8895f", "#694134", "#0e0807", "#ddbb88"],
            ["#d3c8ec", "#867eac", "#393954", "#070710", "#b8aad9"]
        ];
        const colors = palettes[variant];
        // Transparent atmosphere leaves the surrounding void truly black.
        let atmosphere = c.createRadialGradient(x, y, r * .96, x, y, r * 1.075);
        atmosphere.addColorStop(0, colors[1]);
        atmosphere.addColorStop(.38, colors[2]);
        atmosphere.addColorStop(1, "transparent");
        c.fillStyle = atmosphere;
        c.beginPath(); c.arc(x, y, r * 1.075, 0, Math.PI * 2); c.fill();

        c.save();
        c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.clip();
        let surface = c.createRadialGradient(x-r*.48, y-r*.48, 0, x-r*.16, y-r*.12, r*1.25);
        surface.addColorStop(0, colors[0]);
        surface.addColorStop(.35, colors[1]);
        surface.addColorStop(.7, colors[2]);
        surface.addColorStop(1, colors[3]);
        c.fillStyle = surface; c.fillRect(0,0,width,height);

        // Curved cloud belts have fixed, varied contours, not frame-wise noise.
        c.save(); c.translate(x,y); c.rotate(-.26);
        for (let band = 0; band < 22; band++) {
            const by = -r + band * r / 10.5;
            c.beginPath(); c.moveTo(-r*1.2, by);
            c.bezierCurveTo(-r*.5, by-r*.10, r*.4, by+r*.14, r*1.2, by-r*.04);
            c.lineTo(r*1.2, by+3+band%4);
            c.bezierCurveTo(r*.4, by+r*.18, -r*.5, by-r*.06, -r*1.2, by+4);
            c.closePath();
            c.globalAlpha = .07 + band%4 * .025;
            c.fillStyle = band%3 === 0 ? colors[0] : colors[4]; c.fill();
        }
        c.restore();
        // Dark terminator: the unlit hemisphere melts into the void.
        let shadow = c.createLinearGradient(x-r*.8, y-r*.4, x+r*.8, y+r*.3);
        shadow.addColorStop(0, "transparent");
        shadow.addColorStop(.42, "#00000000");
        shadow.addColorStop(.76, "#c9000000");
        shadow.addColorStop(1, "#fa000000");
        c.fillStyle = shadow; c.fillRect(0,0,width,height);
        c.restore();

        // A fine sunlit crescent, without a colored background wash.
        c.strokeStyle = colors[0]; c.globalAlpha = .45; c.lineWidth = 1;
        c.beginPath(); c.arc(x,y,r,Math.PI*.94,Math.PI*1.62); c.stroke();
    }
}
