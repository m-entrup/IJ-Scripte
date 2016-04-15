var Imports = new JavaImporter(
    Packages.ij.IJ,
    Packages.ij.ImagePlus,
    Packages.ij.ImageStack,
    Packages.ij.plugin.Duplicator,
    Packages.ij.measure.CurveFitter);

	
function PixelObject(x, y, valsX, valsY) {
	this.x = x;
	this.y = y;
	this.valsX = valsX;
	this.valsY = valsY;
}

function stackToArray(imp) {		
	with (new JavaImporter(Packages.ij.IJ, Packages.ij.ImagePlus)) {
		var x, y, z, array, elosses, stack, label, pattern, offset, valsY;
		array = [];
		elosses = [];
		stack = imp.getImageStack();
		pattern = /(\d+(\.\d+)?)eV/i;
		offset = parseFloat(pattern.exec(stack.getShortSliceLabel(Math.floor(imp.getStackSize() / 2) + 1)));
		offset = IJ.getNumber("Enter energy loss offset: ", offset);
		if (offset == IJ.CANCELED) {
			return IJ.CANCELED;
		}
		for (z = 0; z < imp.getStackSize(); z++) {
			label = stack.getShortSliceLabel(z+1);
			elosses.push(parseFloat(pattern.exec(label)) - offset);
		}
		for (y = 0; y < imp.getHeight(); y++) {
			for (x = 0; x < imp.getWidth(); x++) {			
				valsY = [];
				for (z = 0; z < imp.getStackSize(); z++) {
					valsY.push(stack.getVoxel(x, y, z));
				}
				array.push(new PixelObject(x, y, elosses, valsY));
			}
		}
		return array;
	}
}
	
function fitGauss(obj) {
	with (Imports) {
		var fit = new CurveFitter(obj.valsX, obj.valsY);
		fit.doFit(CurveFitter.GAUSSIAN);
		obj.offset = fit.getParams()[2];
	}
}
	
function createResultingImp(array, width, height) {
	with (new JavaImporter(Packages.ij.process.FloatProcessor, Packages.ij.ImagePlus)) {
		var fp, imp;
		fp = new FloatProcessor(width, height);
		array.forEach(function(obj) {
			fp.setf(obj.x, obj.y, obj.offset);
		});
		imp = new ImagePlus("NIC", fp);
		return imp;
	}
}
	
function main() {	
	with (Imports) {	
		var inputImp, binnedImp, bin, zProfiles;
		inputImp = IJ.getImage();
		if (inputImp.getStackSize() <= 1) {
			IJ.showMessage("Error", "There must be at least a stack open.");
			return;
		}
		binnedImp = new Duplicator().run(inputImp);
		bin = Math.round(inputImp.getWidth() / 128);
		bin = IJ.getNumber("Set the binning factor:", bin);
		if (bin == IJ.CANCELED) {
			return;
		}
		IJ.run(binnedImp, "Bin...", "x=" + bin + " y=" + bin + " bin=Average");
		zProfiles = stackToArray(binnedImp);
		if (zProfiles == IJ.CANCELED) {
			return;
		}
		zProfiles.forEach(fitGauss);
		createResultingImp(zProfiles, binnedImp.getWidth(), binnedImp.getHeight()).show();
	}
}

main();