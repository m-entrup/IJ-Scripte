x = 192;
y = 192;
w = 128;
h = 128
counts = 1000
stdv = 200
run("Colors...", "foreground=white background=black selection=green");

images = getNumber("Anzahl der zu erzeugnden Bilder:", 3);

newImage("Ref", "32-bit black", 512, 512, 1);
run("Add...", "value=" + counts);
makeRectangle(x, y, w, h);
run("Add...", "value=" + counts);
run("Enhance Contrast", "saturated=0.35");
run("Select None");
run("Add Specified Noise...", "standard=" + stdv);

for (i = 2; i <= images; i++) {
	x_off = round(2 * (random - 0.5) * (x - w/2));
	y_off = round(2 * (random - 0.5) * (y - h/2));
	newImage(x_off + "," + y_off, "32-bit black", 512, 512, 1);
	run("Add...", "value="+ counts);
	makeRectangle(x + x_off, y + y_off, w, h);
	run("Add...", "value=" + counts);
	run("Enhance Contrast", "saturated=0.35");
	run("Select None");run("Add Specified Noise...", "standard=" + stdv);	
}