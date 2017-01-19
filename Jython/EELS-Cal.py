"""
@File(label='Input directory', style='directory') srcDir
"""

from __future__ import with_statement, division

import csv
import os
from exceptions import ValueError

from ij import IJ
from ij.gui import Plot

DEBUG = True
errors = []

class Spectrum:

    @classmethod
    def get_spectrum_csv(cls, csv_file):
        spectrum = []
        with open(csv_file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
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
        if file_path.endswith('.csv'):
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
        from org.apache.commons.math3.util import MathArrays
        reverse = spectrum.ys[::-1]
        corr = MathArrays.convolve(self.ys, reverse)
        new_spec = [{ 'x': x, 'y': y } for x, y in zip(self.xs, corr)]
        return Spectrum(new_spec, self.loss - spectrum.loss)

    def crosscorrelation2(self, spectrum):
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

def pos_of_max(values):
    m = max(values)
    pos = [i for i, j in enumerate(values) if j == m]
    if len(pos) > 1:
        print('Warning: The maximum of the list is not distinct.')
    return pos[0]

def get_shift(spectra):
    ref = spectra[0]
    correlations = [spec.crosscorrelation2(ref) for spec in spectra[1:]]
    if DEBUG:
        for corr in correlations:
            corr.plot()
    xs = [item.loss for item in correlations]
    ys = [pos_of_max(item.ys) for item in correlations]
    xs.append(0)
    ys.append(len(ref.xs) - 1)
    return xs, ys

def get_lin_fit(xs, ys):
    from ij.measure import CurveFitter
    fitter = CurveFitter(xs, ys)
    fitter.doFit(CurveFitter.STRAIGHT_LINE)
    return fitter

def run_script():
    files = []
    for item in os.listdir(srcDir.getAbsolutePath()):
        if str(item).endswith('.csv') or str(item).endswith('.msa'):
            files.append(os.path.join(srcDir.getAbsolutePath(), str(item)))
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
    plot.addLabel(0.75, 0.5, 'dispersion = %f' % (-1/fit.getParams()[1],))
    plot.show()
    for error in errors:
        IJ.log(error)

if __name__ == '__main__':
    run_script()