'''
file:       Calculate_Jump-ratio.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160706
info:       A script that calculates the Jump-Ratio of two images.
            The second image is devided by the first one.
            A drift correction is performed. The first image is shiftet towards to the second one.
'''

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CorrectDrift as drift
import HelperDialogs as dialogs
import Tools as tools

from ij import IJ, WindowManager
from ij.gui import GenericDialog
from ij.plugin import ImageCalculator
from ij.process import ImageStatistics as Stats


def get_setup():
    ''' Returns the drift correction mode and two image.'''
    options = ['Scale-invariant feature transform', 'Normalized cross-correlation']
    modes = ['SIFT', 'CC']
    gd = GenericDialog('Jump-ratio setup')
    gd.addMessage('Select the mode  for drift correction\n' +
        'and the images to process.')
    gd.addChoice('Mode:', options, options[0])
    image_ids = WindowManager.getIDList()
    if not image_ids or len(image_ids) < 2:
        return [None]*3
    image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
    gd.addMessage('Post-edge is divided by the pre-edge.')
    gd.addChoice('Pre-edge', image_titles, image_titles[0])
    gd.addChoice('Post-edge', image_titles, image_titles[1])
    gd.showDialog()
    if gd.wasCanceled():
        return [None]*3
    mode = modes[gd.getNextChoiceIndex()]
    img1 = WindowManager.getImage(image_ids[gd.getNextChoiceIndex()])
    img2 = WindowManager.getImage(image_ids[gd.getNextChoiceIndex()])
    return mode, img1, img2


def run_script():
    selected_mode, img1_in, img2_in = get_setup()
    if not selected_mode:
        return
    corrected_stack = drift.get_corrected_stack((img1_in, img2_in), mode = selected_mode)
    img1, img2 = tools.stack_to_list_of_imp(corrected_stack)
    img_ratio = ImageCalculator().run('Divide create', img2, img1)
    img_ratio.setTitle('Jump-ratio [%s divided by %s]' % (img2.getShortTitle(), img1.getShortTitle()))
    img_ratio.changes = True
    img_ratio.copyScale(img1_in)
    img_ratio.show()
    IJ.run(img_ratio, 'Enhance Contrast', 'saturated=0.35')
    # We want to optimise the lower displaylimit:
    minimum = img_ratio.getProcessor().getMin()
    maximum = img_ratio.getProcessor().getMax()
    stat = img_ratio.getStatistics(Stats.MEAN + Stats.STD_DEV)
    mean = stat.mean
    stdv = stat.stdDev
    if minimum < mean - stdv:
        if mean - stdv >= 0:
            img_ratio.getProcessor().setMinAndMax(mean - stdv, maximum)
        else:
            img_ratio.getProcessor().setMinAndMax(0, maximum)
        img_ratio.updateAndDraw()


if __name__ == '__main__':
    run_script()
