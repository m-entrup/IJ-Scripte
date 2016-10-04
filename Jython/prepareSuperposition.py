# @File(label='Select a aperture file') first_file_pos
# @String(label='File filter position',value='Pos') filter_pos
# @File(label='Select a SR-EELS file') first_file_eels
# @String(label='File filter SR-EELS',value='EELS') filter_eels

"""
Dieses Script wurde erstellt, um für die Bilder im Ordner
Aufnahmen (dm3)\SR-EELS\20151027 Schritt für Schritt zu SR-EELS\5. Variation der Blendenbreite\
Superpositionen für Aufnahmen der Blende und SR_EELS zu erzeugen.
"""

from java.io import File
from ij import IJ

def prepare_superpos(imp):
    imp.setSlice(5)
    IJ.run(imp, 'Delete Slice', '')
    IJ.run(imp, 'Z Project...', 'projection=[Sum Slices]')
    imp.changes = False
    imp.close()
    imp_sum = imp = IJ.getImage()
    bin = 1
    while imp_sum.getWidth() / bin > 1024:
        bin *= 2
    IJ.run(imp, 'Bin...', 'x=%d y=%d bin=Average' % (bin, bin))
    imp_sum.setRoi(256, 256, 512, 512)
    IJ.run(imp_sum, 'Enhance Contrast', 'saturated=0.35')
    IJ.run(imp_sum, "Select None", "")
    return imp_sum

if __name__ == '__main__':
    IJ.run('Image Sequence...',
           'open=[%s] increment=2 file=[%s] sort' % (first_file_pos, filter_pos)
          )
    imp_pos = IJ.getImage()
    imp_pos_sum = prepare_superpos(imp_pos)
    IJ.saveAs(imp_pos_sum,
              'PNG',
              first_file_pos.getParent() + File.separator + 'Blenden_Superposition.png'
              )

    IJ.run('Image Sequence...',
           'open=[%s] increment=2 file=[%s] sort' % (first_file_eels, filter_eels)
          )
    imp_eels = IJ.getImage()
    imp_eels_sum = prepare_superpos(imp_eels)
    IJ.run(imp_eels_sum, 'Rotate 90 Degrees Left', '')

    IJ.saveAs(imp_eels_sum,
              'PNG',
              first_file_eels.getParent() + File.separator + 'SR-EELS_Superposition.png'
             )