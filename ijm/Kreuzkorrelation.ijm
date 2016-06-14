/*
 * file:	Kreuzkorrelation.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20160401
 * info:	Dieses Script berechnet die normierte Kreuzkorrelation von 2 Bildern.
 * 			Die Normierung wird nach der Berechnung der Kreuzkorrelation durchgeführt.
 * 			Das Ergebnis ist ein Bild, welches ScaleBar und CalibrationBar enthält.
 */


var scaleBarColor = "White"; // "White", "Black", ...


checkRequirements(); // Ein Stack mit 2 Bildern ist notwendig.
/*
 * Global variables:
 */
var idResult;
var width = getWidth();
var height = getHeight();

calcNormalisedCrossCorrelation();
styleResult();


function checkRequirements() {
	if (nSlices != 2) {
		showMessage("Abbruch...", "Dieses Macro benötigt einen Stack mit 2 Bildern");
		exit();
	}
}

function calcNormalisedCrossCorrelation() {
	run("Stack to Images");
	id1 = getImageID();
	/*
	 * Es ist notwendig die Bilder neu zu benennen, da Leerzeichen im Titel Probleme verursachen.
	 * Denn getTitle() enthält nur den String bis zum ersten Leerzeichen.
	 */
	rename("img1");
	img1 = getTitle();
	run("Put Behind [tab]");
	id2 = getImageID();
	rename("img2");
	img2 = getTitle();
	//run("Main Window [enter]");
	setBatchMode(true);
	run("FD Math...", "image1=" + img1 + " operation=Correlate image2=" + img2 + " result=Result do");
	idResult = getImageID();
	selectImage(id1);
	run("Square");
	getRawStatistics(nPixels, mean, min, max, std, histogram);
	close(img1);
	norm = sqrt(width) * sqrt(height) * sqrt(mean);
	selectImage(id2);
	run("Square");
	getRawStatistics(nPixels, mean, min, max, std, histogram);
	close(img2);
	norm *= sqrt(width) * sqrt(height) * sqrt(mean);
	selectImage(idResult);
	run("Divide...", "value=" + norm);
	setBatchMode("exit and display");
}

function styleResult() {
	run("Enhance Contrast", "saturated=0.0");
	getMinAndMax(min, max);
	min = round(50 * min) / 50;
	max = round(50 * max) / 50;
	setMinAndMax(min, max);
	if (width < 512) {
		scale = 2;
		while (width * scale < 512) {
			scale *= 2;
		}
		title = getTitle();
		run("Scale...", "x=" + scale + " y=" + scale + " z=1.0 interpolation=None create");
		new = getImageID();
		selectImage(idResult);
		close();
		selectImage(new);
		rename(title);
		width = getWidth;
		height = getHeight;
	}
	run("Remove Overlay");
	makeLine(0.5 * width, 0, 0.5 * width, height);
	run("Add Selection...");
	makeLine(0, 0.5 * height, width, 0.5 * height);
	run("Add Selection...");
	run("Find Maxima...", "noise=" + width / 4 + " output=[Point Selection]");
	run("Add Selection...");
	run("Select None");
	createScaleBar();
	createCalBar();
}

function createScaleBar() {
	fontSize = width / 4096 * 150;
	getPixelSize(unit, pixelWidth, pixelHeight);
	if (width*pixelWidth > 10) {
		barWidth = 10 * round(width*pixelWidth / 80);
	} else if (width*pixelWidth > 1) {
		barWidth = floor((width*pixelWidth / 8) + 1);
	} else {
		barWidth = 0.01 * floor(100 * width*pixelWidth / 8);
	}
	barHeight = fontSize / 3;
	run("Scale Bar...", "width=" + barWidth + " height=" + barHeight + " font=" + fontSize + " color=" + scaleBarColor + " background=None location=[Lower Right] bold overlay");
}

function createCalBar() {
	fontSize = 10;
	zoom = width / 4096 * 10;
	run("Calibration Bar...", "location=[Upper Right] fill=White label=Black number=3 decimal=2 font=" + fontSize + " zoom=" + zoom + " overlay");
}