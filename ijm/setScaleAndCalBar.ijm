/*
 * file:	setScaleAndCalBar.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20151118
 * info:	Dieses Script erzeugt ein 8-bit Bild mit Scale- und Calibrationbar.
 * 			Breite der Scalebar und die Schriftgröße werden automatisch gewählt, die Werte lassen sich aber auch ändern.
 * 			In dem Ursprünglichen Bild werden die Elemente als Overlay eingefügt.
 */

getPixelSize(unit, pixelWidth, pixelHeight);
defaultBarWidth = 10 * round(getWidth*pixelWidth/80);
barWidth = getNumber("ScaleBar Größe (in " + unit + "): ", defaultBarWidth);
defaultFontSize = 10 * round(getHeight/400)
size = getNumber("Schriftgröße: ", defaultFontSize);
sizeCal = size;
zoom = 1;
while (sizeCal > 20) {
	sizeCal /= 2;
	zoom *= 2;
}
height = size / 3;

run("Calibration Bar...", "location=[Upper Right] fill=White label=Black number=3 decimal=0 font=sizeCal zoom=zoom overlay");
run("Scale Bar...", "width=barWidth height=height font=size color=Black background=White location=[Lower Right] overlay");
run("Flatten");