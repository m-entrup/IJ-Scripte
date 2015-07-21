getPixelSize(unit, pixelWidth, pixelHeight);
bar = getNumber("ScaleBar Größe (in " + unit + "): ", 0);
size = 15;
size = getNumber("Schriftgröße: ", size);
if (size > 20) {
	sizeCal = size / 2;
	zoom = 2;
} else {	
	sizeCal = size;
	zoom = 1;
}
height = size / 4;

run("Calibration Bar...", "location=[Upper Right] fill=White label=Black number=3 decimal=0 font=sizeCal zoom=zoom");
run("Scale Bar...", "width=bar height=height font=size color=Black background=White location=[Lower Right]");
