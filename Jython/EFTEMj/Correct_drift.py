"""
file:       Correct_drift.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160706
info:       A script that corrects the drift between two images.
            The images are not changed. A copy of the second image is shifted.
            The normalized cross correlation used for drift detection is displayed.
"""

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import HelperDialogs as dialogs
import CorrectDrift as drift

from ij import IJ, WindowManager
from ij.plugin import Duplicator


def select_images():
    """
    Returns two ImagePlus objects that can be used by the drift correction.
    If more than two images are available a dialog is used for selection.
    """
    if WindowManager.getImageCount() > 0:
        imp = WindowManager.getCurrentImage()
        if imp.getImageStackSize() == 2:
            dup = Duplicator()
            img1 = dup.run(imp, 1, 1)
            img1.setTitle("Slice1")
            img2 = dup.run(imp, 2, 2)
            img2.setTitle("Slice2")
        elif WindowManager.getImageCount() == 2:
            img1, img2 = [WindowManager.getImage(id) for id in WindowManager.getIDList()]
        elif WindowManager.getImageCount() > 2:
            image_ids = WindowManager.getIDList()
            image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
            try:
                sel1, sel2 = dialogs.create_selection_dialog(image_titles, range(2))
            except TypeError:
                return(None, None)
            img1 = WindowManager.getImage(image_ids[sel1])
            img2 = WindowManager.getImage(image_ids[sel2])
        else:
            IJ.error("You need two images to run the script.")
            return(None, None)
    else:
        IJ.error("You need two images to run the script.")
        return(None, None)
    return (img1, img2)


def correct_drift_gui():
    """
    This function combines the image selection and drift correction.
    There is no returned value.
    """
    img1, img2 = select_images()
    if (img1 and img2):
        drift.correct_drift(img1, img2, True)


def run_script():
    correct_drift_gui()


if __name__ == '__main__':
    run_script()
