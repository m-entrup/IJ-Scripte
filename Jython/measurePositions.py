from ij import IJ
from ij.process import ImageStatistics as stats
from ij.measure import ResultsTable

def get_positions(stack):
    cal = stack.getCalibration()
    IJ.setAutoThreshold(stack, 'Default dark')
    IJ.run(stack, 'NaN Background', 'stack')

    measures = stats.CENTROID # alternative: stats.CENTER_OF_MASS
    x_pos = []
    y_pos = []
    name = []
    # Die Positionen sollen sich auf Binning 1 beziehen:
    bin = 4096 / stack.getWidth()
    for n in range(1, stack.getStackSize() + 1):
        stack.setSlice(n)
        x = bin * stack.getStatistics(measures).xCentroid
        y = bin * stack.getStatistics(measures).yCentroid
        x_pos.append(cal.getRawX(x))
        y_pos.append(cal.getRawY(y))
        name.append(stack.getStack().getShortSliceLabel(n))
    return x_pos, y_pos, name

def run_script():
    stack = IJ.getImage()
    if not stack or stack.getStackSize() <= 1:
        return
    x_pos, y_pos, name = get_positions(stack)

    rt = ResultsTable()
    for n in range(stack.getStackSize()):
        rt.incrementCounter()
        rt.addValue('name', name[n])
        rt.addValue('x_pos', x_pos[n])
        rt.addValue('y_pos', y_pos[n])
    rt.show('Position of aperture')

if __name__ == '__main__':
    run_script()