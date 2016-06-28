"""
file:       Correct_drift_(SIFT).py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160628
info:       ...
"""

from pprint import pprint

from java.util import ArrayList, Vector
from java.lang import Float

from ij import IJ, WindowManager, ImageStack, ImagePlus

from mpicbg.imagefeatures import FloatArray2DSIFT, Feature
from mpicbg.ij import SIFT, InverseTransformMapping
from mpicbg.models import TranslationModel2D

class Param:
    sift = FloatArray2DSIFT.Param()
    # Closest/next closest neighbour distance ratio
    rod = 0.92
    #Maximal allowed alignment error in px
    maxEpsilon = 25.0
    # Inlier/candidates ratio
    minInlierRatio = 0.05
    # Implemeted transformation models for choice
    modelStrings = ['Translation,' 'Rigid', 'Similarity', 'Affine']
    modelIndex = 1
    interpolate = True
    showInfo = False

def main():
    p = Param()
    imp = WindowManager.getCurrentImage()
    stack = imp.getStack()
    ip1 = stack.getProcessor(1)
    ip2 = stack.getProcessor(2)
    sift = FloatArray2DSIFT(p.sift)
    fs1 = ArrayList()
    fs2 = ArrayList()
    ijSIFT = SIFT(sift)
    ijSIFT.extractFeatures(ip1, fs1)
    print '%i features extracted from %s' %(len(fs1), stack.getShortSliceLabel(1))
    ijSIFT.extractFeatures(ip2, fs2)
    print '%i features extracted from %s' %(len(fs2), stack.getShortSliceLabel(2))
    model = TranslationModel2D()
    mapping = InverseTransformMapping(model)
    candidates = FloatArray2DSIFT.createMatches( fs2, fs1, 1.5, None, Float.MAX_VALUE, p.rod )
    print '%i potentially corresponding features identified' % len(candidates)
    inliers = Vector()
    model.filterRansac(candidates, inliers, 1000, p.maxEpsilon, p.minInlierRatio)
    """
    transform = [0.0] * 6
    model.toArray(transform)
    pprint(transform)
    """
    print model.createAffine().translateX, model.createAffine().translateY
    alignedSlice = ip2.createProcessor(stack.getWidth(), stack.getHeight())
    mapping.map(ip2, alignedSlice)
    ImagePlus('Corrected', alignedSlice).show()

main()