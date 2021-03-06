﻿# coding=utf-8
"""
file:       HelperDialogs.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160624
info:       This module contains some some dialogs for repetitive tasks.
"""

from __future__ import with_statement, division
from ij import WindowManager
from ij.gui import GenericDialog

def get_image_titles():
    """
    Returns the titles of all open image windows as a list.
    """
    image_ids = WindowManager.getIDList()
    image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
    return image_titles

def get_images(ids):
    """
    Returns a list of ImagePlus objects.
    :param ids: The ids of the ImagePlus objects to return.
    """
    image_ids = WindowManager.getIDList()
    return [WindowManager.getImage(image_ids[id]) for id in ids]

def create_selection_dialog(image_titles, defaults, title='Select images for processing'):
    """
    Show a dialog to select the images to process and return a list of the selected ones (index).
    :param image_titles: A list of image titles presented for selection.
    :param defaults: The titles to be selected by default. The length of this list defines the number of selectable images.
    :param title: the title of the dialog (default 'Select images for processing').
    """
    gd = GenericDialog(title)
    for index, default in enumerate(defaults):
        gd.addChoice('Image_'+ str(index + 1), image_titles, image_titles[default])
    gd.showDialog()
    if gd.wasCanceled():
        return None
    return [gd.getNextChoiceIndex() for _ in defaults]