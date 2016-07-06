'''
file:       Correct_drift_(SIFT).py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160706
info:       A script that corrects the drift between any number of images.
            Scale-invariant feature transform (SIFT) is used for drift detection.
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
import CorrectDrift as drift
import Tools as tools


def run_script():
    images = tools.get_images()
    if not images:
        return
    elif len(images) >= 2:
        corrected_stack = drift.get_corrected_stack(images, 'SIFT')
        corrected_stack.show()


if __name__ == '__main__':
    run_script()
