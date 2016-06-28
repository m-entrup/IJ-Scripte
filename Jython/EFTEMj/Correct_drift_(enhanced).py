"""
file:       Correct_drift_(enhanced).py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160624
info:       A script that corrects the drift between any number of images.
            The images are not changed. A stack is created that holds the corrected images.
"""

from __future__ import with_statement, division
from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CrossCorrelation as CC
import HelperDialogs as dialogs

import operator, copy, pprint
from ij import IJ, WindowManager, ImageStack, ImagePlus
from ij.plugin import Duplicator

def get_drift(i, j, images):
    cc_img = CC.perform_correlation(images[i], images[j])
    offset = CC.get_drift(cc_img)
    """ DEBUG
    print 'Reference: %s at index %i' % (images[i],i)
    print 'Drifted image: %s at index %i' % (images[j],j)
    print 'Offset: %d,%d\n' % offset
    """
    return offset

def perform_func_on_list_of_pairs(func, pair_list):
    xs, ys = zip(*pair_list)
    return (func(xs), func(ys))

def mean_of_list_of_pairs(pair_list):
    def func(vals):
        return sum(vals)/len(vals)
    return perform_func_on_list_of_pairs(func, pair_list)

def center_of_list_of_pairs(pair_list):
    def func(vals):
        return (max(vals) + min(vals)) / 2
    return perform_func_on_list_of_pairs(func, pair_list)

def shift_images(img_list, shift_vector):
    """
    returns a list of new images that are shifted by the given values.
    :param img_list: A list of images to be shifted.
    :param shift_vector: A List of x-, y-coordinates to define the shift per image.
    """
    shifted_list = [Duplicator().run(img) for img in img_list]
    def make_title(i):
        old_title = img_list[i].getTitle()
        new_title = 'DK$%f$%f$%s' % (shift_vector[i][0],shift_vector[i][1], old_title)
        return new_title
    [img.setTitle(make_title(i)) for i, img in enumerate(shifted_list)]
    [IJ.run(img, 'Translate...', 'x=%d y=%d interpolation=None' % (shift_vector[i][0], shift_vector[i][1]))
        for i, img in enumerate(shifted_list)]
    return shifted_list

def main():
    img_count = IJ.getNumber("How many images do you want to correct?", 3)
    # If canceld IJ.getNumber() returns -Integer.MAX_VALUE
    if img_count < 3:
        return False
    image_ids = WindowManager.getIDList()
    image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
    images_selected = dialogs.create_selection_dialog(image_titles, range(img_count), 'Select images for drift correction')
    # dialogs.create_selection_dialog() returns None if canceled
    if not images_selected:
        return False
    images = [WindowManager.getImage(image_ids[selection]) for selection in images_selected]
    drift_matrix = [[]] * len(images)
    for i, _ in enumerate(drift_matrix):
        drift_matrix[i] = [(0,0)] * len(images)
    # print 'Initial matrix: ', drift_matrix
    for i in range(len(images)):
        # print  'i=%i: ' % i, range(i + 1, len(images))
        for j in range(i + 1, len(images)):
            drift = get_drift(i, j, images)
            """ DEBUG
            print 'Appending to %i/%i:' % (i, j)
            print shift
            """
            # print 'Matrix element: ', i, j
            # print 'Adding value: ', drift
            drift_matrix[i][j] = drift
            drift_matrix[j][i] = tuple([-val for val in drift])
    # print 'Drift matrix:'
    # pprint.pprint(drift_matrix)
    centers = [center_of_list_of_pairs(row) for row in drift_matrix]
    # print 'List of centers: ', centers
    mod_matrix = [[tuple(map(operator.sub, cell, centers[i])) for cell in row]
        for i, row in enumerate(drift_matrix)]
    # print 'Modified drift matrix:'
    # pprint.pprint(mod_matrix)
    rot_matrix = [list(x) for x in zip(*mod_matrix)]
    # print 'Rotated matrix:'
    # pprint.pprint(rot_matrix)
    shift_vector = [tuple(map(operator.neg, tup))
        for tup in [mean_of_list_of_pairs(row) for row in rot_matrix]]
    # print 'Optimized shift vector: ', shift_vector
    stack = ImageStack(images[0].getWidth(), images[0].getHeight())
    [stack.addSlice(img.getTitle(), img.getProcessor()) for img in shift_images(images, shift_vector)]
    corrected_stack = ImagePlus('Drift corrected stack', stack)
    corrected_stack.show()

main()