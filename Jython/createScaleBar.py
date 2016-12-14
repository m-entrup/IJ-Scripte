# @ImagePlus input_imp
# @Integer (value='1024') max_width
# @Float(value='0.2') bar_percentage
# @Boolean add_cal_bar

import math

from ij import IJ

def calc_nice_value(value):
    x = math.ceil(math.log10(value)-1)
    pow10x = math.pow(10, x)
    value_rounded = math.ceil(value / pow10x) * pow10x
    return value_rounded

def create_scale(params):
    IJ.run(imp,
           "Scale Bar...",
           "width=%f height=%d font=%d color=Black background=White location=[Lower Left] bold overlay"
           % params
          )

def create_cal(params):
    IJ.run(imp,
           "Calibration Bar...",
           "location=[Upper Right] fill=White label=Black number=3 decimal=0 font=%d zoom=1.5 overlay"
           % params
          )

def main():
    width = imp.getWidth()
    bin = 1
    while bin * max_width < width:
        bin *= 2

    if bin > 1:
        IJ.run(imp, "Bin...", "x=%d y=%d bin=Average" % (bin, bin))
        width /= bin

    bar_width = imp.getCalibration().getX(round(bar_percentage*width))
    bar_width = calc_nice_value(bar_width)
    bar_height = round(bar_percentage * 40)

    font_size = round(bar_percentage * 150)

    bar_params = (bar_width, bar_height, font_size)
    create_scale(bar_params)
    if add_cal_bar:
        cal_params = (round(1. / 2 * font_size),)
        create_cal(cal_params)


if __name__ == '__main__':    
    imp = input_imp.crop()
    main()
    imp.show()