# coding=utf-8
"""
file:        Tools.py
author:        Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20160629
info:        This module contains different usefull functions.
"""

from __future__ import with_statement, division

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')

from ij import ImageStack

def perform_func_on_list_of_tuples(func, list_of_tuples):
    """ Returns a tuple that contains the results of the given function.
    :param func: A function that needs a list as argument.
    :param list_of_tuples: A list that contains tuples, each of the same size.
    """
    # Actually it's a tuple of tuples, but this name reflects how the structure of the construct is changed.
    tuple_of_lists = tuple(zip(*list_of_tuples))
    return tuple(func(item) for item in tuple_of_lists)

def mean_of_list_of_tuples(list_of_tuples):
    """ Returns the mean vector of a list of vectors.
    :param list_of_tuples: The tuples represent vectors (e.g. Points in 2D space).
    """
    def func(vals):
        return sum(vals)/len(vals)
    return perform_func_on_list_of_tuples(func, list_of_tuples)

def center_of_list_of_tuples(list_of_tuples):
    """ Returns the center vector of a list of vectors $c_i = (min_i + max_i) / 2$.
    :param list_of_tuples: The tuples represent vectors (e.g. Points in 2D space).
    """
    def func(vals):
        return (max(vals) + min(vals)) / 2
    return perform_func_on_list_of_tuples(func, list_of_tuples)

def stack_from_list_of_imp(list_of_imps):
    """ Returns an ImageStack that contains the images of the given list.
    :param list_of_imp: A list of ImagePlus objects.
    """
    stack = ImageStack(list_of_imps[0].getWidth(), list_of_imps[0].getHeight())
    [stack.addSlice(img.getTitle(), img.getProcessor()) for img in list_of_imps]
    return stack