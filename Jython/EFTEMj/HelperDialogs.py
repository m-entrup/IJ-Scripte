# coding=utf-8
"""
file:		HelperDialogs.py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160616
info:		This module contains some some dialogs for repetitive tasks.
"""

from __future__ import with_statement, division
from ij import WindowManager
from ij.gui import GenericDialog

def get_image_titles():
	image_ids = WindowManager.getIDList()
	image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
	return image_titles

def get_images(ids):
	image_ids = WindowManager.getIDList()
	return [WindowManager.getImage(image_ids[id]) for id in ids]

def create_selection_dialog(image_titles, defaults, title='Select images for processing'):
	"""
	Show a dialog to select the images to process.
	The length of the list defaults defines the number of selectable images.
	"""
	gd = GenericDialog(title)
	for index, default in enumerate(defaults):
		gd.addChoice('Image_'+ str(index + 1), image_titles, image_titles[default])
	gd.showDialog()
	if gd.wasCanceled():
		return None
	return [gd.getNextChoiceIndex() for _ in defaults]