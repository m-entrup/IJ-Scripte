/*
 * @Integer(label="High image size in px",value=1024) sizeHigh
 * @Integer(label="Raster size in px",value=64) rasterSize
 * @Integer(label="Periode in px",value=512) periode
 * @Integer(label="Periode offset in px",value=32) offsetPeriode
 */

importClass(Packages.ij.IJ);
importClass(Packages.ij.ImagePlus);
importClass(Packages.ij.ImageStack);
importClass(Packages.ij.process.FloatProcessor);
importClass(Packages.ij.gui.Line);
importClass(Packages.ij.plugin.Binner);
importClass(Packages.ij.plugin.Duplicator);
importClass(Packages.ij.plugin.MontageMaker);
importClass(Packages.ij.plugin.frame.RoiManager);


function createHigh(offset) {
	var title = "High" + (offset ? " offset=" + offset : "");
	var off = offset ? offset : 0;
	var impHigh = IJ.createImage(title, "32-bit black", sizeHigh, sizeHigh, 1);
	var fpHigh = impHigh.getProcessor();
	for (var y = 0; y < sizeHigh; y++) {
		for (var x = 0; x < sizeHigh; x++) {
			var value = Math.pow(Math.sin(Math.PI * (x + off) / periode)
						* Math.sin(Math.PI * (y + off) / periode), 2);
			fpHigh.setf(x,y, value);
		}
	}
	impHigh.changes = true;
	return impHigh;
}

function simCam(imp) {
	var impLow = new Duplicator().run(imp);
	impLow = new Binner().shrink(impLow, rasterSize, rasterSize, 1, Binner.AVERAGE);
	IJ.run(impLow, "Size...", "width=" + sizeHigh + " height=" + sizeHigh + " interpolation=None");
	impLow.setTitle(imp.getTitle().replace("High", "Low"));
	return impLow;
}

function createStack(offset) {
	var impHigh = createHigh(offset);
	var impLow = simCam(impHigh);
	var stack = new ImageStack(sizeHigh, sizeHigh, 2);
	stack.addSlice("High", impHigh.getProcessor(), 0);
	stack.addSlice("Low", impLow.getProcessor(), 1);
	return stack;
}

function createMontage(offset) {
	var stack = createStack(offset);
	var impStack = ImagePlus("Stack",  stack);
	var impMontage = new MontageMaker().makeMontage2(impStack, 2, 1, 1, 1, 2, 1, 0, false);
	var title = "Montage" + (offset ? " offset=" + offset : "");
	impMontage.setTitle(title);
	return impMontage;
}

function addGrid(imp) {	
	var roiManager = new RoiManager(true);	
	for (y = 0; y <= sizeHigh; y += rasterSize) {
		roiManager.addRoi(new Line(0, y, sizeHigh, y));
	}
	for (x = 0; x <= sizeHigh; x += rasterSize) {	
		roiManager.addRoi(new Line(x, 0, x, sizeHigh));
	}
	roiManager.runCommand(imp,"Show All without labels");
	return imp.flatten();
}

var montage = createMontage();
montage.show();
IJ.run(montage, "Enhance Contrast", "saturated=0.35");
addGrid(montage).show();

var montageOff = createMontage(offsetPeriode);
montageOff.show();
IJ.run(montageOff, "Enhance Contrast", "saturated=0.35");
addGrid(montageOff).show();