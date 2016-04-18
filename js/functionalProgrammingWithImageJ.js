var IjImport = new JavaImporter(Packages.ij.IJ)

/* Begin of function definitions */

var getPixels = function(image) {
	var objects, pixels, width, height, x, y;
	
	with (IjImport) {			
		if (image) {
			// TODO: Check if image is ImagePlus or ImageProcessor
			pixels = image.getProcessor().getPixels();
		} else {
			pixels = IJ.getImage().getProcessor().getPixels();
			width = IJ.getImage().getWidth();
			height = IJ.getImage().getHeight();
		} 
		objects = [];
		for (y = 0; y < height; y++) {
			for (x = 0; x < width; x++) {
				objects.push( {
					"x": x,
					"y": y,
					"value": parseFloat(pixels[y * width + x])
				});
			}
		}
	}
	return objects;
}

var example = function() {
	var pixels, filtered, values, x, y, r;

	x = 200;
	y = 200;
	r = 50;
	pixels = getPixels();
	print("Pixels in image: " + pixels.length);
	filtered = pixels.filter(function(obj) {
		return (obj.x - x)*(obj.x - x) + (obj.y - y)*(obj.y - y) <= r*r;
	});
	print("Pixels in radius: " + filtered.length);
	values = filtered.map(function(obj) {
		return obj.value;
	});
	print("Mean value in radius: " + values.reduce(function(mean, value, index, array) {
		return mean + value / array.length;
	}, 0));
}

/* End of function definitions */


/* Main Code */
with (IjImport) {		
	var imp = IJ.openImage("http://imagej.nih.gov/ij/images/Cell_Colony.jpg");
	IJ.run(imp, "16-bit", "");
	imp.show();
}
example();
imp.close();