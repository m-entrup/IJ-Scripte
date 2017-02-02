from __future__ import division

import math
import re
import time

from java.lang import Runnable
from java.lang import Runtime
from java.lang import RuntimeException
from java.lang import Thread
from java.lang.reflect import Array
from java.util.concurrent.atomic import AtomicInteger

from ij import IJ
from ij import ImagePlus
from ij.plugin import Duplicator
from ij.process import FloatProcessor

from org.apache.commons.math3.fitting import SimpleCurveFitter
from org.apache.commons.math3.fitting import WeightedObservedPoints
from org.apache.commons.math3.analysis import ParametricUnivariateFunction

pattern_eloss = re.compile('(\d+(?:\.\d+)?)eV')

class ZProfiles:

    def __init__(self, imp, offset):
        self.imp = imp
        self.loss_offset = offset
        self.w = imp.getWidth()
        self.h = imp.getHeight()
        self.index = self.w * self.h
        self.offset = [0] * (self.w * self.h)
        self.width = [0] * (self.w * self.h)
        self.amplitude = [0] * (self.w * self.h)
        self.elosses = []
        self.pixels = []
        for z in range(self.imp.getStackSize()):
            label = self.imp.getStack().getShortSliceLabel(z+1)
            match = pattern_eloss.search(label)
            loss = float(match.group(1)) - self.loss_offset
            self.elosses.append(loss)
            self.pixels.append(self.imp.getStack().getPixels(z + 1))
            IJ.showProgress(z + 1, self.imp.getStackSize())


def create_nic(data):
    fp = FloatProcessor(data.w, data.h)
    for y in range(data.h):
        for x in range(data.w):
            index = x + y * data.w
            fp.setf(index, data.offset[index])
    imp = ImagePlus("NIC", fp)
    return imp

def create_width(data):
    fp =  FloatProcessor(data.w, data.h)
    for y in range(data.h):
        for x in range(data.w):
            index = x + y * data.w
            fp.setf(index, data.width[index])
    imp = ImagePlus("width", fp)
    return imp

def create_amplitude(data):
    fp =  FloatProcessor(data.w, data.h)
    for y in range(data.h):
        for x in range(data.w):
            index = x + y * data.w
            fp.setf(index, data.amplitude[index])
    imp = ImagePlus("amplitude", fp)
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

def fit_gauss(fitter, data, index):
    points = WeightedObservedPoints()
    for i, z in enumerate(data.elosses):
        points.add(1, z, data.pixels[i][index])
    amplitude, offset, width = fitter.fit(points.toList())
    data.offset[index] = offset
    data.width[index] = width
    data.amplitude[index] = amplitude

def multithread_func(func, data):
    threads = Array.newInstance(Thread, Runtime.getRuntime().availableProcessors())
    print('Processing %d profiles with %d threads.' % (data.index, len(threads)))
    ai = AtomicInteger(0)
    progress = AtomicInteger(1)
    class Body(Runnable):

        def __init__(self):
            self.fitter = create_fitter()

        def run(self):
            for i in (ai.getAndIncrement() for _ in  range(data.index)):
                if i < data.index:
                    func(self.fitter, data, i)
                    IJ.showProgress(progress.getAndIncrement(), data.index)
    for i in range(len(threads)):
        threads[i] = Thread(Body())
        threads[i].start()
    for thread in threads:
        thread.join()

def main():
    try:
        inputImp = IJ.getImage()
        if inputImp.getStackSize() <= 1:
            IJ.showMessage("Error", "There must be at least a stack open.")
            return
    except RuntimeException:
        # Exit if IJ.getImage() was not able to return an image.
        return

    # We guess that the stack is sorted by energy loss and that the ZLP is at the centre of the stack.
    offset_match = pattern_eloss.search(
        inputImp.getStack().getShortSliceLabel(
            int(math.floor(inputImp.getStackSize() / 2)) + 1
        )
    )
    offset = float(offset_match.group(1))
    offset = IJ.getNumber("Enter energy loss offset: ", offset)
    if (offset == IJ.CANCELED) :
        return

    IJ.showStatus("Preparing the data...")
    IJ.showProgress(0)
    zProfiles = ZProfiles(inputImp, offset)
    if zProfiles == IJ.CANCELED:
        return
    IJ.showStatus("Calculating the NIC...")
    IJ.showProgress(0)
    start_time = time.time()
    '''
    for profile in zProfiles:
        fit_gauss(zProfiles.fitter, profile)
    '''
    multithread_func(fit_gauss, zProfiles)
    print('Fitting took %.3fs to finish.' % (time.time() - start_time,))
    create_nic(zProfiles).show()
    create_width(zProfiles).show()
    create_amplitude(zProfiles).show()

if __name__ == '__main__':
    main()