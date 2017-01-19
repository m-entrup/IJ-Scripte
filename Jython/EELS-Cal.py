"""
@File(label='Input directory', style='directory') srcDir
@boolean(label='Use fast mode', description='calc in fourier space') fast_mode
@boolean(label='Debug mode') DEBUG
"""

from __future__ import with_statement, division

import csv
import os
from exceptions import ValueError

from ij import IJ
from ij.gui import Plot

errors = []

class Spectrum:

    @classmethod
    def get_spectrum_csv(cls, csv_file):
        spectrum = []
        with open(csv_file, 'rb') as csvfile:
            delim=','
            if csv_file.endswith('.xls'):
                delim='\t'
            reader = csv.reader(csvfile, delimiter=delim)
            for row in reader:
                try:
                    spectrum.append({
                                     'x': float(row[0]),
                                     'y': float(row[1])
                                    })
                except ValueError:
                    errors.append('%s: Skipping this row: %s' % (os.path.basename(csv_file),row))
        return spectrum

    @classmethod
    def get_spectrum_msa(cls, msa_file):
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
    def from_file(cls, file_path):
        if file_path.endswith('.csv') or file_path.endswith('.xls'):
            spectrum = Spectrum.get_spectrum_csv(file_path)
        if file_path.endswith('.msa'):
            spectrum = Spectrum.get_spectrum_msa(file_path)
        import re
        pattern = '.*\D(\d+)eV.*'
        m = re.match(pattern, file_path)
        loss = int(m.group(1))
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
    m = method(values)
    pos = [i for i, j in enumerate(values) if j == m]
    if len(pos) > 1:
        print('Warning: The %s of the list is not distinct.' (method,))
    return pos[0]

def get_shift(spectra):
    ref = spectra[0]
    correlations = [spec.crosscorrelation(ref) for spec in spectra[1:]]
    if DEBUG:
        for corr in correlations:
            corr.plot()
    xs = [item.loss for item in correlations]
    ys = [pos_of(item.ys, max) for item in correlations]
    xs.append(0)
    ys.append(len(ref.xs) - 1)
    return xs, ys

def get_lin_fit(xs, ys):
    from ij.measure import CurveFitter
    fitter = CurveFitter(xs, ys)
    fitter.doFit(CurveFitter.STRAIGHT_LINE)
    return fitter

def error_of_dispersion(fit, xs):
    r2 = [val**2 for val in fit.getResiduals()]
    s_y = sum(r2) / (len(r2) - 2)
    x2s = [val**2 for val in xs]
    dm = s_y**2 * len(r2) / (len(r2) * sum(x2s) - sum(xs)**2)
    return dm / fit.getParams()[1]**2

def run_script():
    files = []
    for item in os.listdir(srcDir.getAbsolutePath()):
        if str(item).endswith('.csv') or str(item).endswith('.xls') or str(item).endswith('.msa'):
            files.append(os.path.join(srcDir.getAbsolutePath(), str(item)))
    if len(files) <= 1:
        return
    spectra = [Spectrum.from_file(csv_file) for csv_file in files]
    spectra = sorted(spectra, key=lambda item: item.loss)
    #spectra[10].crosscorrelation(spectra[0]).plot()
    plot =  Plot('EELS-Cal',
                 'Energy loss difference [eV]',
                 'Shift [px]'
                )
    xs, ys = get_shift(spectra)
    plot.addPoints(xs, ys, Plot.CROSS)
    fit = get_lin_fit(xs, ys)
    x_fit = range(min(xs), max(xs) + 1)
    y_fit = [fit.f(x) for x in x_fit]
    plot.addPoints(x_fit, y_fit, Plot.LINE)
    plot.addLegend('Measured shift\ng(x) = %f x + %f' % (fit.getParams()[1], fit.getParams()[0]))
    plot.addLabel(0.6, 0.4, 'dispersion = %feV/px\n uncertainty: %feV/px' % (-1/fit.getParams()[1],error_of_dispersion(fit, xs)))
    plot.show()
    for error in errors:
        IJ.log(error)

if __name__ == '__main__':
    run_script()