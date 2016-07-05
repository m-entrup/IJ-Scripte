# coding=utf-8
'''
file:       pySIFT.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160705
info:       This module calculates the drift using SIFT.
'''

from __future__ import with_statement, division

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import Tools as tools

import math

from ij import IJ, WindowManager, ImageStack, ImagePlus

from java.util import ArrayList, Vector
from java.lang import Float

from mpicbg.imagefeatures import FloatArray2DSIFT, Feature
from mpicbg.ij import SIFT, InverseTransformMapping
from mpicbg.models import TranslationModel2D

class Param:
    '''A dataset that holds parameters used by the SIFT algorithm.
    You can modify an instance of this object to customize the SIFT detection.
    '''
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

class pySIFT:
    '''An implementation of a drift correction using the SIFT algorithm.
    It is designed to measure the drift of all images with each other.
    '''

    def __init__(self, img_list, params = None):
        '''Create an instance of pySIFT.
        :param img_list: All SIFT calculations are done with the given list of ImagePlus objects (Classes that extend ImagePlus are allowed).#
        :param params: Pass a modified instance of Param to customize the SIFT detection (default: None).
        '''
        self.images = []
        def check(img):
            # Check if the given object extends ImagePlus:
            return ImagePlus().class.isAssignableFrom(img.class)
        for img in img_list:
            if check(img):
                self.images.append(img)
        if params and type(params) == Param:
            self.param = params
        else:
            self.param = Param()
        self.drift_matrix = [[]] * len(self.images)
        for i, _ in enumerate(self.drift_matrix):
            self.drift_matrix[i] = [None] * len(self.images)
        self._extract_features_()

    def _extract_features_(self):
        '''This method is used by the constructor to identify the features of each image.
        '''
        sift = FloatArray2DSIFT(self.param.sift)
        ijSIFT = SIFT(sift)
        self.all_features = [ArrayList() for _ in self.images]
        for img, features in zip(self.images, self.all_features):
            ijSIFT.extractFeatures(img.getProcessor(), features)

    def get_drift(self, index1, index2):
        '''Returns th drift between the images at the given indices.
        :param index1: The index of the first image (0-based).
        :param index2: The index of the second image (0-based).
        '''
        if not self.drift_matrix[index1][index2]:
            if index1 == index2:
                self.drift_matrix[index1][index2] = (0, 0)
            model = TranslationModel2D()
            mapping = InverseTransformMapping(model)
            candidates = FloatArray2DSIFT.createMatches(self.all_features[index1], self.all_features[index2], 1.5, None, Float.MAX_VALUE, self.param.rod)
            # print '%i potentially corresponding features identified' % len(candidates)
            inliers = Vector()
            model.filterRansac(candidates, inliers, 1000, self.param.maxEpsilon, self.param.minInlierRatio)
            self.drift_matrix[index1][index2] = (model.createAffine().translateX, model.createAffine().translateY)
        return self.drift_matrix[index1][index2]

    def get_drift_matrix(self):
        '''Returns a NxN matrix that represents the drift of all images with each other.
        '''
        full_progress = len(self.images)**2
        for i in range(len(self.images)):
            for j in range(len(self.images)):
                IJ.showProgress((i * len(self.images) + j) / full_progress)
                self.drift_matrix[i][j] = self.get_drift(i, j)
        IJ.showProgress(1.0)
        return self.drift_matrix