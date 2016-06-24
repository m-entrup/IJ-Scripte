# coding=utf-8
"""
file:		CorrectDrift.py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160624
info:		This module will correct the drift between two images.
"""

from __future__ import with_statement, division
from ij import IJ, WindowManager, ImagePlus
from ij.plugin import Duplicator

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')

import HelperDialogs as dialogs
import CrossCorrelation as cc

def select_images():
	"""
	Returns two ImagePlus objects that can be used by the drift correction.
	If more than two images are available a dialog is used for selection.
	"""
	if WindowManager.getImageCount() > 0:
		imp = WindowManager.getCurrentImage()
		if imp.getImageStackSize() == 2:
			dup = Duplicator()
			img1 = dup.run(imp, 1, 1)
			img1.setTitle("Slice1")
			img2 = dup.run(imp, 2, 2)
			img2.setTitle("Slice2")
		elif WindowManager.getImageCount() == 2:
			img1, img2 = [WindowManager.getImage(id) for id in WindowManager.getIDList()]
		elif WindowManager.getImageCount() > 2:
			image_ids = WindowManager.getIDList()
			image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
			try:
				sel1, sel2 = dialogs.create_selection_dialog(image_titles, range(2))
			except TypeError:
				return(None, None)
			img1 = WindowManager.getImage(image_ids[sel1])
			img2 = WindowManager.getImage(image_ids[sel2])
		else:
			IJ.error("You need two images to run the script.")
			return(None, None)
	else:
		IJ.error("You need two images to run the script.")
		return(None, None)
	return (img1, img2)

def correct_drift(img1, img2, display_cc=False):
	"""
	Returns two ImagePlus objects that are drift corrected to each other.
	The first image is not changed.
	The second image is a new image that is shifted using ImageJ's Translate.
	:param img1: The reference image.
	:param img2: The image to be shifted.
	:param display_cc: Activate displaying the CrossCorrelation image (default False).
	"""
	result = cc.perform_correlation(img1, img2)
	x, y = cc.get_max(result)
	# style after maximum detection
	if not display_cc:
		result.hide()
	else:
		cc.style_cc(result)
	x_off = x - img2.getWidth() / 2
	y_off = y - img2.getHeight() / 2
	if x_off == 0 and y_off == 0:
		print 'No drift has been detected.'
		return img1, img2
	title = img2.getTitle()
	img2_dk = Duplicator().run(img2)
	img2_dk.setTitle('DK-' + title)
	IJ.run(img2_dk, 'Translate...', 'x=%d y=%d interpolation=None' % (x_off, y_off))
	img2_dk.show()
	return img1, img2_dk

def correct_drift_gui():
	"""
	This function combines the image selection and drift correction.
	There is no returned value.
	"""
	img1, img2 = select_images()
	if (img1 and img2):
		correct_drift(img1, img2, True)
