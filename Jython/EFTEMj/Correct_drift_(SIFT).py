'''
file:       Correct_drift_(SIFT).py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160705
info:       ...
'''

from __future__ import with_statement, division

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import pySIFT
import CorrectDrift as drift
import HelperDialogs as dialogs
import Tools as tools

from pprint import pprint

from java.util import ArrayList, Vector
from java.lang import Float, Class

from ij import IJ, WindowManager, ImageStack, ImagePlus

from mpicbg.imagefeatures import FloatArray2DSIFT, Feature
from mpicbg.ij import SIFT, InverseTransformMapping
from mpicbg.models import TranslationModel2D

'''
    alignedSlice = ip2.createProcessor(stack.getWidth(), stack.getHeight())
    mapping.map(ip2, alignedSlice)
    ImagePlus('Corrected', alignedSlice).show()
'''

def run_script():
    img_count = int(IJ.getNumber('How many images do you want to correct (>=3)?', 3))
    # If canceld IJ.getNumber() returns -Integer.MAX_VALUE
    if img_count < 3:
        return
    images = tools.get_images(exact=img_count)
    if not images:
        IJ.showMessage('Can\'t get the demanded number of images.')
        return
    sift = pySIFT.pySIFT(images)
    ''' DEBUG
    for x in sift.all_features:
        print(x.size())
    '''
    # pprint(sift.get_drift_matrix())
    shift_vector = drift.drift_vector_from_drift_matrix(sift.drift_matrix)
    # print 'Optimized shift vector: ', shift_vector
    stack = tools.stack_from_list_of_imp(drift.shift_images(images, shift_vector))
    corrected_stack = ImagePlus('Drift corrected stack', stack)
    corrected_stack.show()

if __name__ == '__main__':
    run_script()