//---------------8<----------- ------
// Morphological_contrast_Thr
// G. Landini 24/Jun/2013
// Sets the pixel value to either Max or Min, depending on which one is
// the closest and above a set threshold
// Similar to Toggle Contrast in Soille, Morphological Image Analysis (2004),
// p. 259.
// It can use operators other than Min and Max (ie Open and Close, etc)

setBatchMode(true);
if (bitDepth()!=24) {
	a=getTitle();
	Dialog.create("Morphologica Contrast Thr");
	Dialog.addNumber("Radius", 2);
	Dialog.addNumber("Threshold", 25);
	Dialog.show();
	r=Dialog.getNumber();
	t=Dialog.getNumber();

	run("Duplicate...", "title=min");
	run("Minimum...", "radius="+r);
	selectWindow(a);
	run("Duplicate...", "title=max");
	run("Maximum...", "radius="+r);

	selectWindow("max");
	w=getWidth();
	h=getHeight();
	i=0;
	max=newArray(w*h);
	for (x=0;x<w;x++) {
		for (y=0;y<h;y++) {
			max[i]=getPixel(x,y);
			i++;
		}
	}


	selectWindow("min");
	i=0;
	min=newArray(w*h);
	for (x=0;x<w;x++) {
		for (y=0;y<h;y++) {
			min[i]=getPixel(x,y);
			i++;
		}
	}

	selectWindow(a);
	i=0;
	for (x=0;x<w;x++) {
		for (y=0;y<h;y++) {
			c=getPixel(x,y);
			if (max[i]-min[i]>t) {
				if((max[i]-c)<=(c-min[i])) {
					putPixel(x,y, max[i]);
				}
				else if ((max[i]-c)>(c-min[i])) {
					putPixel(x,y, min[i]);
				}
			}
			i++;
		}
	}
	updateDisplay();
	selectWindow("min");
	close();
	selectWindow("max");
	close();
}
else {
	showMessage("Error","Greyscale images only!\nConvert RGB to HSB and process\nthe Brightness channel only.");
}

setBatchMode(false);

//---------------8<----------- ------