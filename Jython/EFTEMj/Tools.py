# coding=utf-8
'''
file:       Tools.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160706
info:       This module contains different usefull functions.
'''

from __future__ import with_statement, division

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import HelperDialogs as dialogs

from ij import IJ, ImagePlus, ImageStack, WindowManager


def perform_func_on_list_of_tuples(func, list_of_tuples):
    ''' Returns a tuple that contains the results of the given function.
    :param func: A function that needs a list as argument.
    :param list_of_tuples: A list that contains tuples, each of the same size.
    '''
    # Actually it's a tuple of tuples, but this name reflects how the structure of the construct is changed.
    tuple_of_lists = tuple(zip(*list_of_tuples))
    return tuple(func(item) for item in tuple_of_lists)


def mean_of_list_of_tuples(list_of_tuples):
    ''' Returns the mean vector of a list of vectors.
    :param list_of_tuples: The tuples represent vectors (e.g. Points in 2D space).
    '''
    def func(vals):
        return sum(vals)/len(vals)
    return perform_func_on_list_of_tuples(func, list_of_tuples)


def center_of_list_of_tuples(list_of_tuples):
    ''' Returns the center vector of a list of vectors $c_i = (min_i + max_i) / 2$.
    :param list_of_tuples: The tuples represent vectors (e.g. Points in 2D space).
    '''
    def func(vals):
        return (max(vals) + min(vals)) / 2
    return perform_func_on_list_of_tuples(func, list_of_tuples)


def stack_from_list_of_imp(list_of_imps):
    ''' Returns an ImageStack that contains the images of the given list.
    :param list_of_imp: A list of ImagePlus objects.
    '''
    stack = ImageStack(list_of_imps[0].getWidth(), list_of_imps[0].getHeight())
    for img in list_of_imps:
        stack.addSlice(img.getTitle(), img.getProcessor())
    return stack


def stack_to_list_of_imp(imp_stack):
    ''' Returns a list of newly created ImagePlus objects.
    :param stack: The ImagePlus containing astack that is converted to a list.
    '''
    size = imp_stack.getStackSize()
    labels = [imp_stack.getStack().getShortSliceLabel(i) for i in range(1, size + 1)]
    ips = [imp_stack.getStack().getProcessor(i) for i in range(1, size + 1)]
    images = [ImagePlus(label, ip) for label, ip in zip(labels, ips)]
    return images


def get_images(minimum=0, maximum=None, exact=None):
    ''' Returns a list of ImagePlus objects or None if it failed.
    Passing None as parameter will trigger a dialog to show up to enter the exact number of images.
    :param minimum: The minimum number of images to select (default: 0).
    :param maximum: The maximum number of images to select (default: None).
    :param exact: Set this to get an exact number of images (default: None).
    '''
    if not (minimum or maximum or exact):
        exact = int(IJ.getNumber("How many images do you want to process?", 3))
    def check_count(count):
        # print count, exact, minimum, maximum
        if exact:
            if not count == exact:
                return False
        else:
            if minimum:
                if count < minimum:
                    return False
            if maximum:
                if count > maximum:
                    return False
        return True

    # Option 1: The selected image is a stack and has the demanded size.
    if check_count(WindowManager.getCurrentImage().getStackSize()):
        return stack_to_list_of_imp(WindowManager.getCurrentImage())

    # Option 2: The count of open images matches the demanded number.
    image_ids = WindowManager.getIDList()
    if exact:
        if len(image_ids) < exact:
            return None
        if len(image_ids) == exact:
            return [WindowManager.getImage(img_id) for img_id in image_ids]

    # Option 3: The user can select the images from a list.
    image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
    img_count = len(image_ids)
    if exact:
        img_count = exact
    elif maximum:
        img_count = maximum
        image_titles.append('None')
    images_selected = dialogs.create_selection_dialog(image_titles, range(img_count), 'Select images for drift correction')
    # dialogs.create_selection_dialog() returns None if canceled
    if not images_selected:
        return None
    # This is only true if 'None has been appended to image_titles and the user selected it.
    if len(image_ids) in images_selected:
        images_selected.remove(len(image_ids))
    if not check_count(len(images_selected)):
        return None
    images = [WindowManager.getImage(image_ids[selection]) for selection in images_selected]
    return images
