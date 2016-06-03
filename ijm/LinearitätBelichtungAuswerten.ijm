dir = getDirectory("Ordner mit Bildern wählen");
setBatchMode(true);
fileList = getFileList(dir);

function getExp(label) {
	code = "var Ausdruck = /Bin\\d_(\\d+(\\.\\d+)?)s/;\n";
	code += "Ausdruck.exec('" + label + "');\n";
	code += "RegExp.$1;";
	return eval("script", code);
}

expArray = newArray();
meanArray = newArray();
showProgress(0);
for (i = 0; i < fileList.length; i++) {
	open(dir + fileList[i]);
	binning = 4096 / getWidth();
	/*
	 * Die Ränder der Bilder enthalten gespiegelte Pixel.
	 * Diese werden durch das Zuschneiden entfernt.
	 */
	if (binning == 8) {
		makeRectangle(1, 1, getWidth() - 2, getHeight() - 2);
		run("Crop");
	} else if (binning == 4) {
		makeRectangle(2, 2, getWidth() - 4, getHeight() - 4);
		run("Crop");
	} else if (binning == 2) {
		makeRectangle(5, 5, getWidth() - 10, getHeight() - 10);
		run("Crop");
	} else if (binning == 1) {
		makeRectangle(10, 10, getWidth() - 20, getHeight() - 20);
		run("Crop");
	}
	getRawStatistics(nPixels, mean, min, max, std, histogram);
	run("Remove Outliers...", "radius=1 threshold=" + (2 * mean) + " which=Dark slice");
	if (3 * mean < 744) {
		mean = 744 / 3;
	}
	run("Remove Outliers...", "radius=1 threshold=" + (3 * mean) + " which=Bright slice");	
	getRawStatistics(nPixels, mean, min, max, std, histogram);
	meanArray = Array.concat(meanArray, mean);
	expArray = Array.concat(expArray, parseFloat(getExp(getTitle())));
	close(getTitle());
	showProgress(i+1, fileList.length);
}

Array.show(expArray, meanArray);
Plot.create("Linearität der Belichtungszeit", "Belichtungszeit [s]", "Counts [a.u.]");
Plot.add("crosses", expArray, meanArray);