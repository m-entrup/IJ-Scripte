importClass(Packages.ij.IJ);
importClass(Packages.ij.ImagePlus);
importClass(Packages.ij.ImageStack);
importClass(Packages.ij.plugin.Duplicator);
importClass(Packages.ij.measure.CurveFitter);

function PixelObject(x, y, valsX, valsY) {
	this.x = x;
	this.y = y;
	this.valsX = valsX;
	this.valsY = valsY;
}

function stackToArray(imp) {
	var x, y, z, array, elosses, stack, label, pattern, offset, valsY;
	array = [];
	elosses = [];
	stack = imp.getImageStack();
	pattern = /(\d+(\.\d+)?)eV/i;
	// We guess that the stack is sorted by energy loss and that the ZLP is at the centre of the stack.
	offset = parseFloat(pattern.exec(stack.getShortSliceLabel(Math.floor(imp.getStackSize() / 2) + 1)));
	offset = IJ.getNumber("Enter energy loss offset: ", offset);
	if (offset == IJ.CANCELED) {
		return IJ.CANCELED;
	}
	IJ.showStatus("Preparing the data...");
	for (z = 0; z < imp.getStackSize(); z++) {
		label = stack.getShortSliceLabel(z+1);
		elosses.push(parseFloat(pattern.exec(label)) - offset);
	}
	/*
	 * Create an object for each pixel of the stacks projection:
	 * Each object represents an EEL spectrum of the ZLP.
	 */
	for (y = 0; y < imp.getHeight(); y++) {
		for (x = 0; x < imp.getWidth(); x++) {
			valsY = [];
			for (z = 0; z < imp.getStackSize(); z++) {
				valsY.push(stack.getVoxel(x, y, z));
			}
			array.push(new PixelObject(x, y, elosses, valsY));
		}
		IJ.showProgress(y+1, imp.getHeight());
	}
	array.width = imp.getWidth();
	array.height = imp.getHeight();
	return array;
}

function export2JSON(array) {
	with (new JavaImporter(Packages.ij.text.TextWindow)) {
		var obj2Export = {
			'width': array.width,
			'height': array.height,
			'zProfiles': array,
			'date': new Date()
		};
		strExport = JSON.stringify(obj2Export, null, ' ');
		textWindow = new TextWindow("JSON export", strExport, 800,600);
		textWindow.show();
	}
}

function fitGauss(obj) {
	var fit = new CurveFitter(obj.valsX, obj.valsY);
	// 4*(1.1*c)^4 = 5.8564*c^4 -> b+/-s contains 68.3% off all values.
	fit.doCustomFit("y = a*exp(-(x-b)*(x-b)*(x-b)*(x-b)/(5.8564*c*c*c*c))", [1e4, 0, 1.4], false);
	obj.offset = fit.getParams()[1];
	obj.width = fit.getParams()[2];
}

function createNicImp(array) {
	with (new JavaImporter(Packages.ij.process.FloatProcessor)) {
		var fp, imp;
		fp = new FloatProcessor(array.width, array.height);
		array.forEach(function(obj) {
			fp.setf(obj.x, obj.y, obj.offset);
		});
		imp = new ImagePlus("NIC", fp);
		return imp;
	}
}

function createWidthImp(array) {
	with (new JavaImporter(Packages.ij.process.FloatProcessor)) {
		var fp, imp;
		fp = new FloatProcessor(array.width, array.height);
		array.forEach(function(obj) {
			fp.setf(obj.x, obj.y, obj.width);
		});
		imp = new ImagePlus("width", fp);
		return imp;
	}
}

function multithreader(fun, array) {
	with (new JavaImporter(Packages.java.lang.Thread)) {
		var threads = java.lang.reflect.Array.newInstance(Thread.class, java.lang.Runtime.getRuntime().availableProcessors());
		var ai = new java.util.concurrent.atomic.AtomicInteger(0);
		var progress = new java.util.concurrent.atomic.AtomicInteger(1);
		var body = {
			run: function() {
				for (var i = ai.getAndIncrement(); i < array.length; i = ai.getAndIncrement()) {
					fun(array[i]);
					IJ.showProgress(progress.getAndIncrement(), array.length);
				}
			}
		}
		// start all threads
		for (var i = 0; i < threads.length; i++) {
				threads[i] = new Thread(new java.lang.Runnable(body)); // automatically as Runnable
				threads[i].start();
		}
		// wait until all threads finish
		for (var i = 0; i < threads.length; i++) {
				threads[i].join();
		}
	}
}

function main() {
	var inputImp, binnedImp, bin, zProfiles, zProfilesExport, textWindow;
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
	IJ.showStatus("Preparing the data...");
	IJ.showProgress(0);
	IJ.run(binnedImp, "Bin...", "x=" + bin + " y=" + bin + " bin=Average");
	zProfiles = stackToArray(binnedImp);
	if (zProfiles == IJ.CANCELED) {
		return;
	}
	if (inputImp.getStackSize() * inputImp.getWidth() * inputImp.getHeight() < Math.pow(2, 24) * bin) {
		IJ.showStatus("Preparing the JSON export...");
		export2JSON(zProfiles);
	}
	IJ.showStatus("Calculating the NIC...");
	IJ.showProgress(0);
	d = new Date();
	multithreader(fitGauss, zProfiles);
	print("Fitting took " + (new Date() - d) / 1000 + "s to finish.");
	createNicImp(zProfiles).show();
	createWidthImp(zProfiles).show();
}

main();