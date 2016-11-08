# @File(label = 'Input directory', style = 'directory') srcFile
# @String(label='Filter', value='ImgSpec') file_filter
# @File(label = 'Output directory', style = 'directory') dstFile

from __future__ import with_statement, division

import os
from ij import IJ, ImagePlus

from java.lang import ArrayIndexOutOfBoundsException

from EFTEMj_pyLib import Tools
from EFTEMj_pyLib import CorrectDrift as drift

def get_energy_loss(imp):
    import re
    pattern = '[\w\_\d]*?(-?\d+(?:[,.]\d+)?)eV[\w\_\d]*'
    m = re.match(pattern, imp.getTitle())
    return float(m.group(1))

class NIC:

    def __init__(self):
        self.images = []
        self.NIC = [None]
        self.drif_vec = []
        self.file_types = ('.dm3',)


    def open_images(self, str_filter):
        list_imps = Tools.batch_open_images(srcFile.getAbsolutePath(),
                                              file_type=self.file_types,
                                              name_filter=str_filter,
                                              recursive=False
                                             )

        self.images = sorted(list_imps, key=get_energy_loss)
        self.NIC = Tools.batch_open_images(srcFile.getAbsolutePath(),
                                           file_type='.tif',
                                           recursive=True
                                          )
        assert len(self.NIC) == 1


    def getLine(self, images, x, y, shift = None):
        if not shift and len(images) > 1:
            '''Für die zu korrigierenden Daten.
            '''
            line = [image.getProcessor().getf(x,y) for image in images]
        if shift and len(images) == 1:
            '''Für einzelnes NIC-Bild.
            Linie wird aus NIC-Bild und Verschiebungen generiert. 
            '''
            def get_pixel(x, y):
                ip = images[0].getProcessor()
                try:
                    val = ip.getf(x, y)
                except IndexError:
                    val = 0
                except ArrayIndexOutOfBoundsException:
                    val = 0
                return val
            line = [get_pixel(int(round(x + dx)), int(round(y + dy))) for dx, dy in shift]
        return line


    def setLine(self, corrected_images, x, y, corrected_line):
        for image,value in zip(corrected_images, corrected_line):
            image.getProcessor().setf(x, y, value)


    def NIC_and_Drift_corrected_line(self, line, NIC_line, energy_line):
        """This function takes one line of the image datacube
        and the accompanying line of the NIC-datacube
        and corrects the acromaticity in this line.
        """
        # Energy-distance between the images
        dE = 1
        # generates a list of 0 with lenght of the line
        new_line = [0 for x in range(len(line))]
        for index, _ in enumerate(line):
            '''corrects the acromaticity for integral numbers of the NIC-line
            or NIC-line-values bigger/(smaller) than 1/(-1)
            '''
            integral_energyshift = int(NIC_line[index] // dE)
            if integral_energyshift > 0 and (index + integral_energyshift) in range(len(line)):
                '''integral energyshift bigger one
                '''
                new_line[index] = line[index+integral_energyshift]
            if integral_energyshift < 0 and (index + integral_energyshift) in range(len(line)):
                '''integral energyshift smaller zero
                '''
                new_line[index] = line[index+integral_energyshift]
            if integral_energyshift == 0:
                '''no integral energy-shift
                '''
                new_line[index] = line[index]
        corrected_line = [0 for x in range(len(new_line))]
        for index,_ in enumerate(new_line):
            '''generates the weight average between two values of the image-line,
            when there are non-integral NIC-line-values
            '''
            # integral energyshift bigger/(smaller) than 1/(-1)
            integral_energyshift = int(NIC_line[index] // dE)
            # non-integral energyshift
            small_energyshift = NIC_line[index] % dE
            if small_energyshift > 0 and ((index + 1) in range(len(line))) and (new_line[index] and new_line[index+1] != 0):
                corrected_line[index] = (1-small_energyshift) * new_line[index] + small_energyshift * new_line[index + 1]
            elif small_energyshift == 0:
                corrected_line[index] = new_line[index]
            elif (small_energyshift > 0 and integral_energyshift < 0 and index == len(new_line) - 1):
                corrected_line[index] = (1 - small_energyshift) * new_line[index] + small_energyshift * line[index+integral_energyshift + 1]
            elif small_energyshift > 0 and ((index + 1) in range(len(line))) and new_line[index + 1] == 0:
                corrected_line [index] = (1 - small_energyshift) * new_line[index] + small_energyshift * line[index+integral_energyshift + 1]
        return corrected_line


    def Drift_and_NIC_correction(self, images, drift_vec, NIC):
        """This function takes the image datacube, a drift vector and the NIC-image
        and generates an acromatic-corrected datacube of ESI-images
        """
        corrected_images = [IJ.createImage(image.getTitle(),
                                           "32-bit black",
                                           image.getWidth(),
                                           image.getHeight(),
                                           1
                                          ) for image in images]
        energy_line = [get_energy_loss(image) for image in images]
        print('Energieverluste: %s' % (energy_line,))
        IJ.showStatus('Creating acromatic-corrected datacube...')
        IJ.showProgress(0)
        for y in range(images[0].getHeight()):
            for x in range(images[0].getWidth()):
                line = self.getLine(images, x ,y)
                NIC_line = self.getLine(NIC, x, y, shift=drift_vec)
                corrected_line = self.NIC_and_Drift_corrected_line(line, NIC_line, energy_line)
                self.setLine(corrected_images, x, y, corrected_line)
            IJ.showProgress(y / images[0].getHeight())
        IJ.showProgress(1.0)
        return corrected_images

def test1():
    nic = NIC()
    Test_line = [4168, 3820, 4241, 4755, 4885, 4789]
    NIC_Test = [-1.1, -0.5, -0.2, 0, 0.6, 1.1]
    energy_test = [0, 1, 2, 3, 4, 5]
    assert(len(Test_line) == len(NIC_Test))#
    result = nic.NIC_and_Drift_corrected_line(Test_line, NIC_Test, energy_test)
    print(result)
    if result != [0, 3994.0, 4568.0, 4755, 4827.4, 0]:
        print("Upps, da passt was nicht")
    else:
        print("Sehr gut, alles ist richtig. Gut gemacht!")

def main():
    nic = NIC()
    nic.open_images(file_filter)
    print(nic.NIC)
    for imp in nic.images:
        print(imp)
    '''
    nic.drift_vec = drift.get_drift_vector_sift(nic.images)
    for vec in nic.drift_vec:
        print(vec)
    '''
    nic.drift_vec = [(0.0, 0.0),
                     (-0.5206480083616327, 0.5351080035384257),
                     (-1.8140419819321494, 0.638837111555631),
                     (-1.9035087200479381, 0.9107342136104535),
                     (-1.9227944604469371, 1.9856290737739073),
                     (-2.327765760778391, 2.278571323972983)
                    ]
    list_corrected = nic.Drift_and_NIC_correction(nic.images, nic.drift_vec, nic.NIC)
    for imp in list_corrected:
        imp.show()
    IJ.run(None, "Images to Stack", "")

if __name__ == '__main__':
     test1()
     main()