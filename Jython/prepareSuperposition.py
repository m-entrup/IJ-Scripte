# @File(label='Select a aperture file') first_file_pos
# @String(label='File filter position',value='(^Pos)') filter_pos
# @File(label='Select a SR-EELS file') first_file_eels
# @String(label='File filter SR-EELS',value='(^EELS)') filter_eels

"""
Dieses Script wurde erstellt, um für die Bilder im Ordner
Aufnahmen (dm3)\SR-EELS\20151027 Schritt für Schritt zu SR-EELS\5. Variation der Blendenbreite\
Superpositionen für Aufnahmen der Blende und SR_EELS zu erzeugen.
"""

from java.io import File
from java.awt import Font
from ij import IJ
from ij.gui import Roi, Arrow, TextRoi

def prepare_superpos(imp):
    imp.setSlice(5)
    IJ.run(imp, 'Delete Slice', '')
    IJ.run(imp, 'Z Project...', 'projection=[Max Intensity]')
    imp.changes = False
    imp.close()
    imp_sum = imp = IJ.getImage()
    w, h = imp.getWidth(), imp.getHeight()
    imp.setRoi(int(w/4), int(w/4), int(w/2), int(w/2))
    IJ.run(imp, 'Enhance Contrast', 'saturated=0.35')
    IJ.run("Select None", "")
    return imp_sum

def bin_image(imp):
    bin = 1
    while imp.getWidth() / bin > 1024:
        bin *= 2
    IJ.run(imp, 'Bin...', 'x=%d y=%d bin=Average' % (bin, bin))

def draw_arrows(imp):
    w, h = imp.getWidth(), imp.getHeight()
    IJ.run("Arrow Tool...", "width=20 size=144 color=White style=Notched")
    font = Font("SansSerif", Font.BOLD, 144)
    arrow = Arrow(200, 200, 1200, 200)
    arrow.setStrokeWidth(20)
    imp.setRoi(arrow)
    IJ.run(imp, "Draw", "slice")
    imp.setRoi(TextRoi(1200, 250, "y", font))
    IJ.run(imp, "Draw", "slice")
    IJ.run(imp, 'Rotate 90 Degrees Left', '')
    arrow = Arrow(200, h - 200, 1200, h - 200)
    arrow.setStrokeWidth(20)
    imp.setRoi(arrow)
    IJ.run(imp, "Draw", "slice")
    imp.setRoi(TextRoi(1200, h - 250, "Energieverlust", font))
    IJ.run(imp, "Draw", "slice")

if __name__ == '__main__':
    IJ.run('Image Sequence...',
           'open=[%s] increment=2 file=[%s] sort' % (first_file_pos, filter_pos)
          )
    imp_pos = IJ.getImage()
    imp_pos_sum = prepare_superpos(imp_pos)
    bin_image(imp_pos_sum)
    IJ.saveAs(imp_pos_sum,
              'PNG',
              first_file_pos.getParent() + File.separator + 'Blenden_Superposition.png'
              )

    IJ.run('Image Sequence...',
           'open=[%s] increment=2 file=[%s] sort' % (first_file_eels, filter_eels)
          )
    imp_eels = IJ.getImage()
    w, h = imp_eels.getWidth(), imp_eels.getHeight()
    imp_eels.setRoi(int(w/4), int(w/4), int(w/2), int(w/2))
    imp_eels_crop = imp_eels.duplicate()
    IJ.run("Select None", "")
    imp_eels_sum = prepare_superpos(imp_eels)
    draw_arrows(imp_eels_sum)
    bin_image(imp_eels_sum)
    IJ.saveAs(imp_eels_sum,
              'PNG',
              first_file_eels.getParent() + File.separator + 'SR-EELS_Superposition.png'
             )
    imp_eels_crop_sum = prepare_superpos(imp_eels_crop)
    bin_image(imp_eels_crop_sum)
    IJ.run(imp_eels_crop_sum, 'Rotate 90 Degrees Left', '')
    IJ.saveAs(imp_eels_crop_sum,
              'PNG',
              first_file_eels.getParent() + File.separator + 'SR-EELS_Superposition_Ausschnitt.png'
             )