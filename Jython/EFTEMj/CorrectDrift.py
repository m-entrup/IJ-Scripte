# coding=utf-8
'''
file:       CorrectDrift.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160706
info:       This module will correct the drift between two images.
'''

from __future__ import with_statement, division

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CrossCorrelation as cc
import pySIFT
import Tools as tools

import operator, pprint, math

from ij import IJ, ImagePlus
from ij.plugin import Duplicator


def correct_drift(img1, img2, display_cc=False):
    ''' Returns two ImagePlus objects that are drift corrected to each other.
    The first image is not changed.
    The second image is a new image that is shifted using ImageJ's Translate.
    :param img1: The reference image.
    :param img2: The image to be shifted.
    :param display_cc: Activate displaying the CrossCorrelation image (default False).
    '''
    result = cc.perform_correlation(img1, img2)
    x_off, y_off = cc.get_shift(result)
    # style after maximum detection
    if not display_cc:
        result.hide()
    else:
        cc.style_cc(result)
    if x_off == 0 and y_off == 0:
        print('No drift has been detected.')
        return img1, img2
    title = img2.getTitle()
    img2_dk = Duplicator().run(img2)
    img2_dk.setTitle('DK-' + title)
    IJ.run(img2_dk, 'Translate...', 'x=%d y=%d interpolation=None' % (x_off, y_off))
    img2_dk.show()
    return img1, img2_dk


def get_corrected_stack(images, mode = 'CC'):
    ''' Returns a drift corrected stack using the given method for drift detection.
    :param images: A list containing ImagePlus objects.
    :param mode: The method used for drift detection (e.g. CC, SIFT).
    '''
    drift_matrix = get_drift_matrix(images, mode)
    corrected_stack = get_corrected_stack_using_matrix(images, drift_matrix, mode)
    return corrected_stack


def get_drift_matrix(images, mode = 'CC'):
    ''' Returns the drift matrix of the given Images.
    For N images a NxN matrix is created.
    :param images: A list containing ImagePlus objects.
    :param mode: The method used for drift detection (e.g. CC, SIFT).
    '''
    if mode == 'CC':
        return get_drift_matrix_cc(images)
    elif mode == 'SIFT':
        return get_drift_matrix_sift(images)
    return None


def get_drift_matrix_cc(images):
    ''' Returns the drift matrix of the given images.
    Cross correlation is used for drift detection.
    :param images: A list containing ImagePlus objects.
    '''
    def get_drift(i, j, images):
        cc_img = cc.perform_correlation(images[i], images[j])
        offset = cc.get_drift(cc_img)
        ''' DEBUG
        print 'Reference: %s at index %i' % (images[i],i)
        print 'Drifted image: %s at index %i' % (images[j],j)
        print 'Offset: %d,%d\n' % offset
        '''
        return offset
    images = cc.scale_to_power_of_two(images)
    drift_matrix = [[]] * len(images)
    for i, _ in enumerate(drift_matrix):
        drift_matrix[i] = [(0,0)] * len(images)
    # print 'Initial matrix: ', drift_matrix
    for i in range(len(images)):
        # print  'i=%i: ' % i, range(i + 1, len(images))
        for j in range(i + 1, len(images)):
            img_drift = get_drift(i, j, images)
            ''' DEBUG
            print 'Appending to %i/%i:' % (i, j)
            print shift
            '''
            # print 'Matrix element: ', i, j
            # print 'Adding value: ', drift
            drift_matrix[i][j] = img_drift
            drift_matrix[j][i] = tuple([-val for val in img_drift])
    # print 'Drift matrix:'
    # pprint(drift_matrix)
    return drift_matrix


def get_drift_matrix_sift(images):
    ''' Returns the drift matrix of the given images.
    Scale-invariant feature transform is used for drift detection.
    :param images: A list containing ImagePlus objects.
    '''
    sift = pySIFT.pySIFT(images)
    ''' DEBUG
    for x in sift.all_features:
        print(x.size())
    '''
    # pprint(sift.get_drift_matrix())
    return sift.get_drift_matrix()



def get_corrected_stack_using_vector(images, drift_vector, suffix = ''):
    ''' Returns a drift corrected stack using the given drift vector.
    :param images: A list of length N containing ImagePlus objects.
    :param drift_matrix: A list of length N that contains the measured drift.
    '''
    stack = tools.stack_from_list_of_imp(shift_images(images, drift_vector))
    title = 'Drift corrected stack'
    if suffix:
        title += ' (%s)' % (suffix)
    corrected_stack = ImagePlus(title, stack)
    return corrected_stack


def get_corrected_stack_using_matrix(images, drift_matrix, suffix = ''):
    ''' Returns a drift corrected stack using the given drift matrix.
    :param images: A list of length N containing ImagePlus objects.
    :param drift_matrix: A NxN matrix that contains the measured drift between N images.
    '''
    drift_vector =  drift_vector_from_drift_matrix(drift_matrix)
    return get_corrected_stack_using_vector(images, drift_vector, suffix)


def drift_vector_from_drift_matrix(drift_matrix):
    ''' Returns a list of tuples that represents the optimized drift vector.
    :param drift_matrix: A NxN matrix that contains the measured drift between N images.
    '''
    barycenters = [tools.mean_of_list_of_tuples(row) for row in drift_matrix]
    # print 'List of centers: ', centers
    mod_matrix = [[tuple(map(operator.sub, cell, barycenters[i])) for cell in row]
        for i, row in enumerate(drift_matrix)]
    # print 'Modified drift matrix:'
    # pprint.pprint(mod_matrix)
    rot_matrix = [list(x) for x in zip(*mod_matrix)]
    # print 'Rotated matrix:'
    # pprint.pprint(rot_matrix)
    shift_vector = [tuple(map(operator.neg, tup))
        for tup in [tools.mean_of_list_of_tuples(row) for row in rot_matrix]]
    return shift_vector


def shift_images(img_list, shift_vector):
    ''' Returns a list of new images that are shifted by the given values.
    It is necessary to round down the shift values as ImageJ can only translate by integer values.
    :param img_list: A list of images to be shifted.
    :param shift_vector: A List of x-, y-coordinates to define the shift per image.
    '''
    shift_vector = [(math.floor(shift[0]), math.floor(shift[1])) for shift in shift_vector]
    shifted_list = [Duplicator().run(img) for img in img_list]
    def make_title(i):
        old_title = img_list[i].getTitle()
        new_title = 'DK#%d&%d#%s' % (shift_vector[i][0],shift_vector[i][1], old_title)
        return new_title
    for i, img in enumerate(shifted_list):
        img.setTitle(make_title(i))
    for i, img in enumerate(shifted_list):
        IJ.run(img, 'Translate...', 'x=%d y=%d interpolation=None' % (shift_vector[i][0], shift_vector[i][1]))
    return shifted_list
