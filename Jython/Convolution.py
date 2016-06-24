from __future__ import division
from org.apache.commons.math3.util import MathArrays
from ij.gui import Plot
from java.awt import Color

spec = [5254.975,5029.508,4823.201,4610.067,4431.507,4241.868,4072.098,3897.643,3739.190,3592.498,3447.267,3318.922,3189.036,3077.856,3023.334,3123.553,3162.002,3143.035,3117.522,3004.264,2971.499,2970.035,3091.339,3312.566,3527.791,3700.628,3652.595,3499.127,3347.250,3254.827,3212.112,3157.469,3091.655,3032.771,2982.005,2938.131,2890.961,2839.383,2776.649,2713.609,2655.945,2598.779,2544.316,2485.626,2430.221,2377.389,2333.940,2299.759,2262.659,2357.925,2371.078,2381.128,2403.182,2282.235,2238.074,2193.042,2145.038,2108.918,2075.560,2041.955,2007.901]
energy = [450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600,605,610,615,620,625,630,635,640,645,650,655,660,665,670,675,680,685,690,695,700,705,710,715,720,725,730,735,740,745,750]

def make_slit(array_in, width):
	size = len(array_in)
	array_out = range(size)
	for val in array_out:
		if (val > size/2 - width/2) and val < (size/2 + width/2):
			array_out[val] = 1
		else:
			array_out[val] = 0
	return array_out

slit = make_slit(spec, 20)

conv = MathArrays.convolve(spec, slit)
print len(conv), conv

plot = Plot("Faltung", "Channel", "Wert")
plot.addPoints(range(len(conv)), conv, Plot.LINE)
plot.setColor(Color.RED)
plot.addPoints(range(len(slit)/2, len(conv) - len(slit)/2), [20*val for val in spec], Plot.LINE)
plot.show()