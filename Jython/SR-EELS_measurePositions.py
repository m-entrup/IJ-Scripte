"""
@File(label='Select a aperture file') first_file_pos
@String(label='File filter position',value='(^Pos)') filter_pos
@File(label='Select a SR-EELS file') first_file_eels
@String(label='File filter SR-EELS',value='(^EELS)') filter_eels
@Boolean(label='Rotate SR-EELS', value=False) do_rotate

Dieses Script wertet die Position der Rundblende in der Filtereintrittsebene,
sowie Position und Breite der resultierende SR-EEL Spektrn aus.
"""

from __future__ import division, with_statement

from ij import IJ
from ij.process import ImageStatistics as stats

def process_at(imp, pos):
    """Gibt zwei Listen mit Position und Breite des SR-EEL Spektrums zurück.
    :param imp: ein SR-EEL Spektrum.
    :param pos: Position auf der Energieachse (0,...,1).
    """
    w = imp.getWidth()
    h = imp.getHeight()
    # Wie groß der zu betrachtende Ausschnitt ist:
    sec = h / 10
    # Für die Ränder müssen wir den Offset anpassen:
    if pos * h < sec / 2:
        y_off = 0
    elif pos * h > h - sec / 2:
        y_off = h - sec
    else:
        # Pos ist in der Mitte von sec:
        y_off = pos * h - sec / 2
    imp.setRoi(0, int(y_off), w, int(sec))
    x_pos = []
    width = []
    intensity = []
    mean = []
    bin = 4096 / imp.getWidth()
    for n in range(1, imp.getStackSize() + 1):
        # Threshhold modifiziert alle Bilder des Stacks,
        # weshalb wir jede Iteration einen neuen Stack erzeugen:
        dup = imp.duplicate()
        dup.setSlice(n)
        IJ.setAutoThreshold(dup, 'Li dark')
        IJ.run(dup, 'NaN Background', 'stack')
        measures = stats.CENTROID + stats.INTEGRATED_DENSITY
        x_pos.append(bin * dup.getStatistics(measures).xCentroid)
        # Nur Pixel, die nicht NaN sind werden gezählt:
        width.append(bin * dup.getStatistics(measures).pixelCount / sec)
        intensity.append(dup.getStatistics(measures).pixelCount * dup.getStatistics(measures).mean)
        mean.append(dup.getStatistics(measures).mean)
        dup.close()
    return x_pos, width, intensity , mean


if __name__ == '__main__':
    IJ.run('Image Sequence...',
           'open=[%s] file=[%s] sort' % (first_file_pos, filter_pos)
          )
    imp_pos = IJ.getImage()
    # Von Interesse sind nur die Pixel-Positionen:
    IJ.run(imp_pos, 'Properties...', 'unit=[] pixel_width=1 pixel_height=1 voxel_depth=1')
    IJ.run('Image Sequence...',
           'open=[%s] file=[%s] sort' % (first_file_eels, filter_eels)
          )
    imp_eels = IJ.getImage()
    if do_rotate:
    	IJ.run(imp_eels, "Rotate 90 Degrees Right", "")
    # Von Interesse sind nur die Pixel-Positionen:
    IJ.run(imp_eels, 'Properties...', 'unit=[] pixel_width=1 pixel_height=1 voxel_depth=1')

    # Mit Hilfe eines Gauss-Filters wird Rauschen reduziert.
    IJ.run(imp_pos, "Gaussian Blur...", "sigma=2 stack")
    IJ.run(imp_eels, "Gaussian Blur...", "sigma=2 stack")

	# Das Spektrum mit der Nr. 12 enthält einen Hellen Spot, der die Auswertung stört.
    imp_eels.setSlice(12)
    IJ.run(imp_eels, "Remove Outliers...", "radius=5 threshold=150 which=Bright")
    imp_eels.setSlice(1)

    # Bei den Aufnahmen der Blenden reicht der Threshold vom ersten Bild.
    IJ.setAutoThreshold(imp_pos, 'Li dark')
    IJ.run(imp_pos, 'NaN Background', 'stack')

    measures = stats.CENTROID # alternative: stats.CENTER_OF_MASS
    x_pos = []
    y_pos = []
    # Die Positionen sollen sich auf Binning 1 beziehen:
    bin = 4096 / imp_pos.getWidth()
    for n in range(1, imp_pos.getStackSize() + 1):
        imp_pos.setSlice(n)
        x_pos.append(bin * imp_pos.getStatistics(measures).xCentroid)
        y_pos.append(bin * imp_pos.getStatistics(measures).yCentroid)

    # Dies sind die Positionen auf der Energieachse in %:
    pos_list = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    # Die Ergebnisse der Auswertung der SR-EEL Spektren landen in einem Dictionary:
    eels_res = {}
    for pos in pos_list:
        eels_x_pos, eels_width, eels_int, eels_mean = process_at(imp_eels, pos / 100)
        # Die Keys werden automatisch generiert:
        eels_res['pos' + str(pos)] = eels_x_pos
        eels_res['width' + str(pos)] = eels_width
        eels_res['int' + str(pos)] = eels_int
        eels_res['mean' + str(pos)] = eels_mean

    # Zuletzt werden alle ergebnisse in eine Tabelle geschrieben:
    from ij.measure import ResultsTable
    rt = ResultsTable()
    for n in range(imp_pos.getStackSize()):
        rt.incrementCounter()
        rt.addValue('x-pos', x_pos[n])
        rt.addValue('y-pos', y_pos[n])
        for key in eels_res.keys():
            rt.addValue(key, eels_res[key][n])
    rt.show('Result')