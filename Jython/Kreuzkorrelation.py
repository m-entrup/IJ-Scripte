"""
file:		Kreuzkorrelation.py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160614
info:		Dieses Script berechnet die normierte Kreuzkorrelation von 2 Bildern.
			Die Normierung wird nach der Berechnung der Kreuzkorrelation durchgeführt.
			Das Ergebnis ist ein Bild, welches ScaleBar und CalibrationBar enthält.
"""
from __future__ import division
import math
from ij import IJ, WindowManager, ImagePlus
from ij.measure import Calibration as Cal
from ij.process import ImageStatistics as Stats
from ij.gui import GenericDialog, Line
from ij.plugin import FFTMath, Duplicator
from java.lang import Integer

"""
Show a dialog to select the images to process.
The length of the list defaults defines the number of selectable images.
"""
def create_selection_dialog(image_titles, defaults):
	gd = GenericDialog("Select images for correlation");
	for index, default in enumerate(defaults):
		gd.addChoice("Image_"+ str(index + 1), image_titles, image_titles[default])
	gd.showDialog()
	if gd.wasCanceled():
		return [0 for _ in defaults]
	return [gd.getNextChoiceIndex() for _ in defaults]


def perform_correlation(img1, img2):
	norm = 1
	for img in (img1, img2):
		copy = img.duplicate()
		img.show()
		IJ.run(copy, "Square", "");
		stat = copy.getStatistics(Stats.MEAN)
		norm *= math.sqrt(stat.umean) * math.sqrt(img.getWidth()) * math.sqrt(img.getHeight())
	#cc = FFTMath()
	#cc.doMath(img1, img2)
	IJ.run(img1, "FD Math...", "image1=" + img1.getTitle() + " operation=Correlate image2=" + img2.getTitle() + " result=Result do");
	result = WindowManager.getImage("Result")
	IJ.run(result, "Divide...", "value=" + str(norm))
	IJ.run(result, "Enhance Contrast", "saturated=0.0")
	return result


def style_cc(cc_img):
	new = ""
	stat = cc_img.getStatistics(Stats.MIN_MAX)
	min = round(50 * stat.min) / 50
	max = round(50 * stat.max) / 50
	cc_img.getProcessor().setMinAndMax(min, max)
	if cc_img.getWidth() < 512:
		scale = 2
		while cc_img.getWidth() * scale < 512:
			scale *= 2
		title = cc_img.getTitle()
		new = IJ.run(cc_img, "Scale...", "x=" + scale + " y=" + scale + " z=1.0 interpolation=None create");
		cc_img.close()
		new.rename(title)
		cc_img = new
	width = cc_img.getWidth()
	height = cc_img.getHeight()
	IJ.run(cc_img, "Remove Overlay", "");
	cc_img.setRoi(Line(0.5 * width, 0, 0.5 * width, height))
	IJ.run(cc_img, "Add Selection...", "");
	cc_img.setRoi(Line(0, 0.5 * height, width, 0.5 * height))
	IJ.run(cc_img, "Add Selection...", "")
	IJ.run(cc_img, "Find Maxima...", "noise=" + str(width / 4) + " output=[Point Selection]")
	IJ.run(cc_img, "Add Selection...", "");
	IJ.run(cc_img, "Select None", "");
	createScaleBar(cc_img)
	createCalBar(cc_img)


def createScaleBar(imp):
	width = imp.getWidth()
	fontSize = width / 4096 * 150
	scaleBarColor = "White"
	cal = imp.getCalibration()
	pixelWidth = cal.getX(1.)
	if width*pixelWidth > 10:
		barWidth = 10 * round(width*pixelWidth / 80)
	elif (width*pixelWidth > 1):
		barWidth = floor((width*pixelWidth / 8) + 1)
	else:
		barWidth = 0.01 * floor(100 * width*pixelWidth / 8)

	barHeight = fontSize / 3
	#print(barWidth, barHeight, fontSize, scaleBarColor)
	IJ.run(imp, "Scale Bar...", "width=%d height=%d font=%d color=%s background=None location=[Lower Right] bold overlay" % (barWidth, barHeight, fontSize, scaleBarColor))


def createCalBar(imp):
	fontSize = 10;
	zoom = imp.getWidth() / 4096 * 10;
	IJ.run(imp, "Calibration Bar...", "location=[Upper Right] fill=White label=Black number=3 decimal=2 font=%d zoom=%d overlay" % (fontSize, zoom));


if WindowManager.getImageCount() > 0:
	imp = WindowManager.getCurrentImage()
	if imp.getImageStackSize() == 2:
		dup = Duplicator()
		img1 = dup.run(imp, 1, 1)
		img1.setTitle("Slice1")
		img2 = dup.run(imp, 2, 2)
		img2.setTitle("Slice2")
		result = perform_correlation(img1, img2)
		style_cc(result)
		[img.close() for img in (img1, img2)]
	elif WindowManager.getImageCount() == 2:
		img1, img2 = [WindowManager.getImage(id) for id in WindowManager.getIDList()]
		result = perform_correlation(img1, img2)
		style_cc(result)
	elif WindowManager.getImageCount() > 2:
		image_ids = WindowManager.getIDList()
		image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
		sel1, sel2 = create_selection_dialog(image_titles, range(2))
		#print(sel1, sel2)
		#print(image_titles[sel1], image_titles[sel2])
		img1 = WindowManager.getImage(image_ids[sel1])
		img2 = WindowManager.getImage(image_ids[sel2])
		result = perform_correlation(img1, img2)
		style_cc(result)
	else:
		IJ.error("You need two images to run the script.")
else:
	IJ.error("You need two images to run the script.")
