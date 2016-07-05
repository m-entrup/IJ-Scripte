'''
file:       Correct_drift_(enhanced).py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160629
info:       A script that corrects the drift between any number of images.
            The images are not changed. A stack is created that holds the corrected images.
'''

from __future__ import with_statement, division

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CrossCorrelation as CC
import CorrectDrift as drift
import HelperDialogs as dialogs
import Tools as tools

from pprint import pprint
from ij import IJ, WindowManager, ImagePlus
from ij.plugin import Duplicator

def get_drift(i, j, images):
    cc_img = CC.perform_correlation(images[i], images[j])
    offset = CC.get_drift(cc_img)
    ''' DEBUG
    print 'Reference: %s at index %i' % (images[i],i)
    print 'Drifted image: %s at index %i' % (images[j],j)
    print 'Offset: %d,%d\n' % offset
    '''
    return offset

def run_script():
    img_count = int(IJ.getNumber("How many images do you want to correct (>=3)?", 3))
    # If canceld IJ.getNumber() returns -Integer.MAX_VALUE
    if img_count < 3:
        return
    images = tools.get_images(exact=img_count)
    if not images:
        IJ.showMessage("Can't get the demanded number of images.")
        return
    images = CC.scale_to_power_of_two(images)
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
    shift_vector = drift.drift_vector_from_drift_matrix(drift_matrix)
    # print 'Optimized shift vector: ', shift_vector
    stack = tools.stack_from_list_of_imp(drift.shift_images(images, shift_vector))
    corrected_stack = ImagePlus('Drift corrected stack', stack)
    corrected_stack.show()

if __name__ == '__main__':
    run_script()