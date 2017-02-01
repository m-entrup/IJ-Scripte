from __future__ import division

import math
import re

from java.lang import RuntimeException

from ij import IJ
from ij import ImagePlus
from ij.plugin import Duplicator
from ij.process import FloatProcessor

from org.apache.commons.math3.fitting import SimpleCurveFitter
from org.apache.commons.math3.fitting import WeightedObservedPoints
from org.apache.commons.math3.analysis import ParametricUnivariateFunction

class PixelObject:

    def __init__(self, x, y, vals_x, vals_y):
        self.x = x
        self.y = y
        self.vals_x = vals_x
        self.vals_y = vals_y
        self.points = WeightedObservedPoints()
        for x, y in zip(vals_x, vals_y):
            self.points.add(1, x, y)
        self.offset = 0
        self.width = 0
        self.amplitude = 0

class ImageArray(list):

    def __init__(self, imp):
        self.width = imp.getWidth()
        self.height = imp.getHeight()

def stack_to_array(imp):
    array = ImageArray(imp)
    elosses = []
    stack = imp.getImageStack()
    pattern = re.compile('(\d+(?:\.\d+)?)eV')

    # We guess that the stack is sorted by energy loss and that the ZLP is at the centre of the stack.
    offset_match = pattern.search(stack.getShortSliceLabel(int(math.floor(imp.getStackSize() / 2)) + 1))
    offset = float(offset_match.group(1))
    offset = IJ.getNumber("Enter energy loss offset: ", offset)
    if (offset == IJ.CANCELED) :
        return IJ.CANCELED
    
    IJ.showStatus("Preparing the data...")
    for z in range(imp.getStackSize()):
        label = stack.getShortSliceLabel(z+1)
        match = pattern.search(label)
        elosses.append(float(match.group(1)) - offset)
        
    '''
    Create an object for each pixel of the stacks projection:
    Each object represents an EEL spectrum of the ZLP.
    '''
    for y in range(imp.getHeight()):
        for x in range(imp.getWidth()):
            valsY = []
            for z in range(imp.getStackSize()):
                valsY.append(stack.getVoxel(x, y, z))
            array.append(PixelObject(x, y, elosses, valsY))
        IJ.showProgress(y+1, imp.getHeight())
    return array

def create_nic(array):
    fp = FloatProcessor(array.width, array.height)
    for obj in array:
        fp.setf(obj.x, obj.y, obj.offset)
    imp = ImagePlus("NIC", fp)
    return imp

def create_width(array):
    fp =  FloatProcessor(array.width, array.height)
    for obj in array:
        fp.setf(obj.x, obj.y, obj.width)
    imp = ImagePlus("width", fp)
    return imp

class Zlp(ParametricUnivariateFunction):

    def value(self, x, parameters):
        a, m, s = parameters
        return a * math.exp(-(x - m)**4/(4 * (1.1 * s)**4))

    def gradient(self, x, parameters):
        a, m, s = parameters
        da = math.exp(-(m - x)**4 / (4 * (1.1 * s)**4))
        dm = -(m - x)**3 * self.value(x, parameters) / (1.1 * s)**4
        ds = (m - x)**4 * self.value(x, parameters) / (1.1 * s)**5
        return [da, dm, ds]

def create_fitter():
    func = Zlp()
    params_start = [1e4, 0, 1.4]
    fitter = SimpleCurveFitter.create(func, params_start)
    return fitter

def fit_gauss(fitter, obj):
    obj.amplitude, obj.offset, obj.width = fitter.fit(obj.points.toList())

def main():
    try:
        inputImp = IJ.getImage()
        if inputImp.getStackSize() <= 1:
            IJ.showMessage("Error", "There must be at least a stack open.")
            return
    except RuntimeException:
        # Exit if IJ.getImage() was not able to return an image.
        return

    binnedImp = Duplicator().run(inputImp)
    bin = round(inputImp.getWidth() / 128)
    bin = int(IJ.getNumber("Set the binning factor:", bin))
    if bin == IJ.CANCELED:
        return
    IJ.showStatus("Preparing the data...")
    IJ.showProgress(0)
    IJ.run(binnedImp, "Bin...", "x=%d y=%d bin=Average" % (bin, bin))
    zProfiles = stack_to_array(binnedImp)
    if zProfiles == IJ.CANCELED:
        return
    IJ.showStatus("Calculating the NIC...")
    IJ.showProgress(0)
    fitter = create_fitter()
    for profile in zProfiles:
        fit_gauss(fitter, profile)
    create_nic(zProfiles).show()
    create_width(zProfiles).show()

if __name__ == '__main__':
    main()