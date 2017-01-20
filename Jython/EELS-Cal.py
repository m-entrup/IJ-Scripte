"""
@File(label='Input directory', style='directory') srcDir
@boolean(label='Use fast mode', description='calc in fourier space') fast_mode
@boolean(label='Debug mode') DEBUG

file:       EELS-Cal.py
author:     Michael Entrup b. Epping (michael.entrup@wwu.de)
version:    20170120
info:       A script to get the energy dispersion from a series of spectra.
"""

from __future__ import with_statement, division

import csv
import os
from exceptions import ValueError

from ij import IJ
from ij.gui import Plot
from ij.gui import ProfilePlot

errors = [] # Save errors to this list and desplay them at the end of the script.

class Spectrum:

    @classmethod
    def get_spectrum_csv(cls, csv_file):
        """ Load from csv files created with ImageJ.
        These files use commas as delimiter.
        Comments are ignored by catching ValueErrors.
        """
        spectrum = []
        with open(csv_file, 'rb') as csvfile:
            delim=','
            if csv_file.endswith('.xls'):
                delim='\t'
            reader = csv.reader(csvfile, delimiter=delim)
            index = 0
            for row in reader:
                try:
                    spectrum.append({
                                     'x': index,
                                     'dE': float(row[0]),
                                     'y': float(row[1])
                                    })
                    index += 1
                except ValueError:
                    errors.append('%s: Skipping this row: %s' % (os.path.basename(csv_file),row))
        return spectrum

    @classmethod
    def get_spectrum_msa(cls, msa_file):
        """ Load from msa files created with Gatan DM.
        These files use commas as delimiter.
        Comments are ignored by catching ValueErrors.
        """
        spectrum = []
        with open(msa_file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            index = 0
            for row in reader:
                try:
                    spectrum.append({
                                     'x': index,
                                     'dE': float(row[0]),
                                     'y': float(row[1])
                                    })
                    index += 1
                except ValueError:
                    errors.append('%s: Skipping this row: %s' % (os.path.basename(msa_file),row))
        return spectrum

    @classmethod
    def get_spectrum_dm3(cls, dm3_file):
        """ Load from dm3 files created with Gatan DM.
        These files are images that are converted to line profiles.
        """
        spectrum = []
        imp = IJ.openImage(dm3_file)
        IJ.run(imp, "Select All", "")
        profiler = ProfilePlot(imp)
        plot = profiler.getPlot()
        ys = plot.getYValues()
        spectrum = []
        index = 0
        for y in ys:
            spectrum.append({
                             'x': index,
                             'y': y
                            })
            index += 1
        return spectrum

    @classmethod
    def from_file(cls, file_path):
        """ Load a spectrum from file and return it as an instance of Spectrum.
        """
        if file_path.endswith('.dm3'):
            spectrum = Spectrum.get_spectrum_dm3(file_path)
        elif file_path.endswith('.csv') or file_path.endswith('.xls'):
            spectrum = Spectrum.get_spectrum_csv(file_path)
        elif file_path.endswith('.msa'):
            spectrum = Spectrum.get_spectrum_msa(file_path)
        else:
            return
        ''' Find an energy loss with optional decimal places.
        The rest of the file name is ignored.
        '''
        import re
        pattern = '.*[^\d\.]((?:\d+[\.,])?\\d+)eV.*'
        m = re.match(pattern, file_path)
        loss = float(m.group(1))
        return cls(spectrum, loss)

    def __init__(self, spectrum, loss):
        self.spec = spectrum

        self.loss = loss
        self.xs = [item['x'] for item in spectrum]
        self.ys = [item['y'] for item in spectrum]

    def plot(self):
        plot =  Plot('Spectrum %deV' % self.loss,
                     'Position [px]',
                     'Intensity [a.u.]',
                     self.xs, self.ys
                    )
        plot.show()

    def crosscorrelation(self, spectrum):
        """ Calculate the crosscorrelation of the instance with a given Spectrum.
        The result is again an instance of Spectrum.
        There are to modes to use:
        1. 'fast_mode' runs in fourier space.
        2. The second mode runs without fouriertransform.
        """
        if fast_mode:
            '''old version
            from org.apache.commons.math3.util import MathArrays
            reverse = spectrum.ys[::-1]
            corr = MathArrays.convolve(self.ys, reverse)
            '''
            from org.apache.commons.math3.transform import FastFourierTransformer
            from org.apache.commons.math3.transform import DftNormalization as norm
            from org.apache.commons.math3.transform import TransformType as trans_type
            transformer = FastFourierTransformer(norm.STANDARD)
            fft1 = transformer.transform(self.ys, trans_type.FORWARD)
            fft2 = transformer.transform(spectrum.ys, trans_type.FORWARD)
            fft2c = [val.conjugate() for val in fft2]
            corr_fft = [val1.multiply(val2) for val1, val2 in zip(fft1, fft2c)]
            corr_c = transformer.transform(corr_fft, trans_type.INVERSE)
            corr = [val.getReal() for val in corr_c]
        else:
            from collections import deque
            from org.apache.commons.math3.stat.correlation import PearsonsCorrelation
            correlator = PearsonsCorrelation()
            corr = []
            shifted = deque(spectrum.ys)
            for i in range(len(self.ys)):
                corr.append(correlator.correlation(self.ys, list(shifted)))
                shifted.rotate(1)
        new_spec = [{ 'x': x, 'y': y } for x, y in zip(self.xs, corr)]
        return Spectrum(new_spec, self.loss - spectrum.loss)

def pos_of(values, method):
    """Find the position of a value that is calculated by the given method.
    """
    m = method(values)
    pos = [i for i, j in enumerate(values) if j == m]
    if len(pos) > 1:
        print('Warning: The %s of the list is not distinct.' (method,))
    return pos[0]

def get_shift(spectra):
    """ Use crosscorrelation do determine the shoft between two spectra.
    The results are two arrays that contain the shift in eV (from title) and in px (from crosscorrelation).
    """
    ref_pos = int(round(len(spectra) / 2))
    ref = spectra[ref_pos]
    if DEBUG:
        IJ.log('Energy loss of the reference spectrum is %deV' % ref.loss)
    correlations = [ref.crosscorrelation(spec) for spec in spectra]
    if DEBUG:
        for corr in correlations:
            corr.plot()
    xs = [item.loss for item in correlations]
    ys = [pos_of(item.ys, max) if item.loss <= 0 else -(len(item.ys) - pos_of(item.ys, max)) for item in correlations]
    xs = xs
    ys = ys
    return xs, ys

def get_lin_fit(xs, ys):
    """Calculate a linear fit for the given values and return it.
    """
    from ij.measure import CurveFitter
    fitter = CurveFitter(xs, ys)
    fitter.doFit(CurveFitter.STRAIGHT_LINE)
    return fitter

def error_of_dispersion(fit, xs):
    """ Calculate the statistical error of the dispersion.
    """
    r2 = [val**2 for val in fit.getResiduals()]
    s_y = sum(r2) / (len(r2) - 2)
    x2s = [val**2 for val in xs]
    dm = s_y**2 * len(r2) / (len(r2) * sum(x2s) - sum(xs)**2)
    return dm / fit.getParams()[1]**2

def run_script():
    files = []
    for item in os.listdir(srcDir.getAbsolutePath()):
        files.append(os.path.join(srcDir.getAbsolutePath(), str(item)))
    if len(files) <= 1:
        return
    spectra = [Spectrum.from_file(file_path) for file_path in files]
    spectra = [spec for spec in spectra if spec is not None]
    if len(spectra) <= 1:
        return
    spectra = sorted(spectra, key=lambda item: item.loss)
    if DEBUG:
        for spec in spectra:
            spec.plot()
    plot =  Plot('EELS-Cal of %s' % os.path.basename(srcDir.getAbsolutePath()),
                 'Energy loss difference [eV]',
                 'Shift [px]'
                )
    xs, ys = get_shift(spectra)
    plot.addPoints(xs, ys, Plot.CROSS)
    fit = get_lin_fit(xs, ys)
    x_fit = range(min(xs), max(xs) + 1)
    y_fit = [fit.f(x) for x in x_fit]
    plot.addPoints(x_fit, y_fit, Plot.LINE)
    plot.addPoints([0], [0], Plot.LINE) # This is necessary to get a new row at the legend
    plot.addLegend('Measured shift\ng(x) = %f x + %f\nr^2 = %f' % (fit.getParams()[1], fit.getParams()[0], fit.getRSquared()))
    plot.addLabel(0.6, 0.4, 'dispersion = %feV/px\n uncertainty: %feV/px\nGatan dispersion: %f' % (-1/fit.getParams()[1],error_of_dispersion(fit, xs), -15 * fit.getParams()[1]))
    plot.show()
    if DEBUG:
        if len(errors) >= 1:
            IJ.log('Errors durring script execution:')
            for error in errors:
                IJ.log(error)

if __name__ == '__main__':
    run_script()