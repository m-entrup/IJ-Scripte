﻿# coding=utf-8
"""
file:		CrossCorrelation.py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160624
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
	"""
	Return an ImagePlus that represents the normalized CrossCorrelation of two images.
	:param img1: The ImagePlus to be used as reference.
	:param img2: The ImagePlus its correlation to the first ImagePlus is calculated.
	"""
	norm = 1
	for img in (img1, img2):
		copy = img.duplicate()
		img.show()
		IJ.run(copy, "Square", "");
		stat = copy.getStatistics(Stats.MEAN)
		norm *= math.sqrt(stat.umean) * math.sqrt(img.getWidth()) * math.sqrt(img.getHeight())
	# Include image names in square brackets to handle file names with spaces.
	suffix = 1
	prefix = 'Result'
	title = prefix
	while WindowManager.getImage(title):
		title = prefix + '-' + str(suffix)
		suffix += 1
	IJ.run(img1, "FD Math...", "image1=[" + img1.getTitle() + "] operation=Correlate image2=[" + img2.getTitle() + "] result=[" + title + "]  do");
	"""
	Alternative to IJ.run where no configuration is possible:
	cc = FFTMath()
	cc.doMath(img1, img2)
	"""
	result = WindowManager.getImage(title)
	IJ.run(result, "Divide...", "value=" + str(norm))
	IJ.run(result, "Enhance Contrast", "saturated=0.0")
	return result


def style_cc(cc_img):
	"""
	Styles an ImagePlus that shows a CrossCorrelation.
	The maximum is marked by a point selection.
	Scale bar and intensity calibration are added.
	:param cc_img: An ImagePlus that shows a CrossCorrelation.
	"""
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
	__create_scalebar(cc_img)
	__create_calbar(cc_img)
	if not cc_img.isVisible():
		cc_img.show()

def get_max(cc_img):
	"""
	Finds the maximum of an image and returns it as a list of the length 2.
	This function is designed for use on CrossCorrelation images.
	:param cc_img: An ImagePlus showing a CrossCorrelation.
	"""
	width = cc_img.getWidth()
	IJ.run(cc_img, "Find Maxima...", "noise=" + str(width / 4) + " output=[Point Selection]")
	roi = cc_img.getRoi()
	if roi.getClass() == PointRoi:
		return (roi.getBounds().x, roi.getBounds().y)
	else:
		return (None, None)

def get_shift(cc_img):
	"""
	Finds the maximum of an image and returns the offset to the centre.
	This function is designed for use on CrossCorrelation images.
	:param cc_img: An ImagePlus showing a CrossCorrelation.
	"""	
	x, y = get_max(cc_img)
	x_off = x - cc_img.getWidth() / 2
	y_off = y - cc_img.getHeight() / 2
	return x_off, y_off

def __create_scalebar(imp):
	"""
	Creates a scale bar and adds it to an ImagePlus. Nothing is returned.
	:param imp: The imagePlus the scale bar is added to.
	"""
	width = imp.getWidth()
	fontSize = width / 4096 * 150
	scaleBarColor = "White"
	cal = imp.getCalibration()
	pixelWidth = cal.getX(1.)
	if width*pixelWidth > 10:
		barWidth = 10 * round(width*pixelWidth / 80)
	elif (width*pixelWidth > 1):
		barWidth = math.floor((width*pixelWidth / 8) + 1)
	else:
		barWidth = 0.01 * math.floor(100 * width*pixelWidth / 8)

	barHeight = fontSize / 3
	#print(barWidth, barHeight, fontSize, scaleBarColor)
	IJ.run(imp, "Scale Bar...", "width=%d height=%d font=%d color=%s background=None location=[Lower Right] bold overlay" % (barWidth, barHeight, fontSize, scaleBarColor))


def __create_calbar(imp):
	"""
	Creates a calibration bar and adds it to an ImagePlus. Nothing is returned.
	:param imp: The imagePlus the calibration bar is added to.
	"""
	fontSize = 10;
	zoom = imp.getWidth() / 4096 * 10;
	IJ.run(imp, "Calibration Bar...", "location=[Upper Right] fill=White label=Black number=3 decimal=2 font=%d zoom=%d overlay" % (fontSize, zoom));
