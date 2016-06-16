# coding=utf-8
"""
file:		CrossCorrelation.py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160616
info:		This module calculates the normalised Cross-correlation of two images.
			There are aditional functions to style the result or find the position of the maximum.
"""

from __future__ import with_statement, division
import math
from ij import IJ, WindowManager, ImagePlus
from ij.measure import Calibration as Cal
from ij.process import ImageStatistics as Stats
from ij.gui import Line, PointRoi
from ij.plugin import FFTMath
from java.lang import Integer

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

def get_max(cc_img):
	width = cc_img.getWidth()
	IJ.run(cc_img, "Find Maxima...", "noise=" + str(width / 4) + " output=[Point Selection]")
	roi = cc_img.getRoi()
	if roi.getClass() == PointRoi:
		return roi.getBounds().x, roi.getBounds().y
	else:
		return None, None


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
