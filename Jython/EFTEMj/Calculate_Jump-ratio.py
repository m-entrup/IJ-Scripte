"""
file:       Calculate_Jump-ratio.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160616
info:       A script that calculates the Jump-Ratio of two images.
            The second image is devided by the first one.
            A drift correction is performed. The first image is shiftet towards to the second one.
"""

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CorrectDrift as drift
import HelperDialogs as dialogs

from ij import IJ
from ij.plugin import ImageCalculator
from ij.process import ImageStatistics as Stats

def run_script():
    img_titles = dialogs.get_image_titles()
    if len(img_titles) < 2:
        return
    selected_ids = dialogs.create_selection_dialog(img_titles, range(2))
    if not selected_ids:
        return
    img1, img2 = dialogs.get_images(selected_ids)
    img2, img1 = drift.correct_drift(img2, img1, False)
    img_ratio = ImageCalculator().run("Divide create", img2, img1)
    img_ratio.setTitle('Jump-ratio [%s divided by %s]' % (img2.getShortTitle(), img1.getShortTitle()))
    img_ratio.changes = True
    img_ratio.show()
    IJ.run(img_ratio, "Enhance Contrast", "saturated=0.35")
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
