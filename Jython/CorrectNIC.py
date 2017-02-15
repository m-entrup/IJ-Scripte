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
    print(imp.getTitle())
    pattern = '[\w\s\_\d]*?(-?\d+(?:[,.]\d+)?)eV[\w\s\_\d]*'
    m = re.match(pattern, imp.getTitle())
    return float(m.group(1))


def crop_stack(stack,drift_vec):
    extremal_drift_vectors = (min(drift_vec,key=lambda x: x[0])[0],min(drift_vec,key=lambda x: x[1])[1],max(drift_vec,key=lambda x: x[0])[0],max(drift_vec,key=lambda x: x[1])[1])
    crop_position = []
    crop_position.append(int(round(-extremal_drift_vectors[0] if extremal_drift_vectors[0] <= 0 else 0)))
    crop_position.append(int(round(-extremal_drift_vectors[1] if extremal_drift_vectors[1] <= 0 else 0)))
    crop_position.append(int(round(stack.getWidth()-(extremal_drift_vectors[2] if extremal_drift_vectors[2] >=0 else 0) - crop_position[0] )))
    crop_position.append(int(round(stack.getHeight()-(extremal_drift_vectors[3] if extremal_drift_vectors[3] >=0 else 0) - crop_position[1] )))

    stack.setRoi(*crop_position)
    stack1 = stack.duplicate()
    stack1.show()


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
                                           name_filter='NIC',
                                           recursive=True
                                          )
        print(len(self.NIC))
        assert len(self.NIC) == 1


    def getLine(self, images, x, y, shift = None):
        def get_pixel(x, y, ip):
            if x >= ip.getWidth():
                return 0
            try:
                val = ip.getf(x, y)
            except IndexError:
                val = 0
            except ArrayIndexOutOfBoundsException:
                val = 0
            return val
        if shift and len(images) > 1:
            '''Für die zu korrigierenden Daten.
            '''
            line = []
            for index,image in enumerate(images):
                dx,dy = shift[index]
                line.append(get_pixel(int(round(x + dx)), int(round(y + dy)),image.getProcessor()))
        if shift and len(images) == 1:
            '''Für einzelnes NIC-Bild.
            Linie wird aus NIC-Bild und Verschiebungen generiert.
            '''

            line = [get_pixel(int(round(x + dx)), int(round(y + dy)),images[0].getProcessor()) for dx, dy in shift]
        return line


    def setLine(self, corrected_images, x, y, corrected_line):
        for image,value in zip(corrected_images, corrected_line):
            image.getProcessor().setf(x, y, value)


    def NIC_and_Drift_corrected_line(self, line, NIC_line):
        """This function takes one line of the image datacube
        and the accompanying line of the NIC-datacube
        and corrects the acromaticity in this line.
        """
        assert len(line)==len(NIC_line)
        # generates a list of 0 with lenght of the line
        new_line = [0 for x in range(len(line))]

        #integral_energyshift = int(NIC_line[index] // dE)
        #small_energyshift = NIC_line[index] % dE

        corrected_line = [0 for x in range(len(line))]

        for index, _ in enumerate(line):
            integral_energyshift = int(NIC_line[index] // self.dE)
            small_energyshift = NIC_line[index] % self.dE

            if small_energyshift == 0:
                if integral_energyshift > 0 and (index + integral_energyshift) in range(len(line)):
                    '''integral energyshift bigger one'''
                    corrected_line[index] = line[index+integral_energyshift]
                elif integral_energyshift < 0 and (index + integral_energyshift) in range(len(line)):
                    '''integral energyshift smaller zero'''
                    corrected_line[index] = line[index+integral_energyshift]
                elif integral_energyshift == 0:
                    '''no integral energy-shift'''
                    corrected_line[index] = line[index]
                else:
                    corrected_line[index] = 0
            else:
                if integral_energyshift >= 0 and (index+1+integral_energyshift) in range (len(line)) and line[index+integral_energyshift] != 0 and line[index+1+integral_energyshift] != 0:
                    ''''''
                    corrected_line[index] = (1-small_energyshift) * line[index+integral_energyshift] + small_energyshift * line[index+1+integral_energyshift]
                elif integral_energyshift < 0 and (index+integral_energyshift) in range(len(line)) and line[index+integral_energyshift] != 0 and line[index+1+integral_energyshift] != 0:
                    ''''''
                    corrected_line[index] = (1-small_energyshift) * line[index+integral_energyshift] + small_energyshift * line[index+1+integral_energyshift]
                else:
                    corrected_line[index] = 0
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
        self.energy_line = [get_energy_loss(image) for image in images]
        # Energy-distance between the images
        self.dE = self.energy_line[1] - self.energy_line[0]
        print('Energieverluste: %s' % (self.energy_line,))
        IJ.showStatus('Creating acromatic-corrected datacube...')
        IJ.showProgress(0)
        for y in range(images[0].getHeight()):
            for x in range(images[0].getWidth()):
                line = self.getLine(images, x ,y,shift=drift_vec)
                NIC_line = self.getLine(NIC, x, y, shift=drift_vec)
                corrected_line = self.NIC_and_Drift_corrected_line(line, NIC_line)
                self.setLine(corrected_images, x, y, corrected_line)
            IJ.showProgress(y / images[0].getHeight())
        IJ.showProgress(1.0)
        return corrected_images


def test1():
    nic = NIC()
    Test_line = [4168, 3820, 4241, 4755, 4885, 4789]
    NIC_Test = [-1.1, -0.5, -0.2, 0, 0.6, 1.1]
    nic.energy_line = [0, 1, 2, 3, 4, 5]
    nic.dE = nic.energy_line[1] - nic.energy_line[0]
    assert(len(Test_line) == len(NIC_Test))#
    result = nic.NIC_and_Drift_corrected_line(Test_line, NIC_Test)
    print(result)
    if result != [0, 3994.0, 4156.8, 4755, 4827.4, 0]:
        print("Upps, da passt was nicht")
        return False
    else:
        print("Sehr gut, alles ist richtig. Gut gemacht!")
        return True


def main():
    nic = NIC()
    nic.open_images(file_filter)
    print(nic.NIC)
    for imp in nic.images:
        print(imp)
    #'''
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
    '''
    list_corrected = nic.Drift_and_NIC_correction(nic.images, nic.drift_vec, nic.NIC)

    title = "NIC-Corrected stack"
    title1 = "NIC-Corrected stack (Cropped)"
    title0 = "Original Stack"
    stack = ImagePlus(title, Tools.stack_from_list_of_imp(list_corrected))
    mid = stack.getStackSize() // 2
    stack.setSlice(mid)
    IJ.run(stack, "Enhance Contrast", "saturated=0.35")
    stack.copyScale(nic.images[0])
    stack.getCalibration().pixelDepth = nic.dE
    stack.getCalibration().zOrigin = -nic.energy_line[0] / nic.dE
    stack.show()

    #'''stack1 = ImagePlus(title1, Tools.stack_from_list_of_imp(list_corrected))
    #stack1.setSlice(mid)
    #IJ.run(stack1, "Enhance Contrast", "saturated=0.35")
    #stack1.copyScale(nic.images[0])
    #stack1.getCalibration().pixelDepth = nic.dE
    #stack1.getCalibration().zOrigin = -nic.energy_line[0] / nic.dE
    #stack1.show()'''

    crop_stack(stack,nic.drift_vec)

    stack0 = ImagePlus(title0, Tools.stack_from_list_of_imp(nic.images))
    stack0.copyScale(nic.images[0])
    stack0.getCalibration().pixelDepth = nic.dE
    stack0.getCalibration().zOrigin = -nic.energy_line[0] / nic.dE
    stack0.show()


if __name__ == '__main__':
     if test1():
         main()