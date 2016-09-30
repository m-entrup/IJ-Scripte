x = 600;
y = 600;
w = 3000;
h = 3000;
stdv = 32

images = getNumber("Anzahl der zu erzeugnden Bilder:", 3);

showProgress(0);
setBatchMode(true);
run("Nile Bend (1.9M)");
run("32-bit");
source = getImageID()
showProgress(1 / images);

makeRectangle(x, y, w, h);
run("Duplicate...", " ");
run("Select None");run("Add Specified Noise...", "standard=" + stdv);	
run("Enhance Contrast", "saturated=0.35");
rename("Ref");

for (i = 2; i <= images; i++) {
	x_off = round(2 * (random - 0.5) * x);
	y_off = round(2 * (random - 0.5) * y);
	selectImage(source);
	makeRectangle(x + x_off, y + y_off, w, h);
	run("Duplicate...", " ");
	run("Select None");run("Add Specified Noise...", "standard=" + stdv);	
	run("Enhance Contrast", "saturated=0.35");
	rename(x_off + "," + y_off);
	showProgress(i / images);
}

selectImage(source);
close();
setBatchMode("exit and display");