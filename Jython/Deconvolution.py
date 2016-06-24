from __future__ import division
import math
from org.apache.commons.math3.complex import Complex
from org.apache.commons.math3.transform import FastFourierTransformer, DftNormalization, TransformType
from jarray import array
from ij.gui import Plot
from java.awt import Color

def pad(vals):
	N = 2
	while N <= len(spec):
		N *= 2
	vals += [0] * (N - len(vals))
	return vals

spec = [5254.975,5029.508,4823.201,4610.067,4431.507,4241.868,4072.098,3897.643,3739.190,3592.498,3447.267,3318.922,3189.036,3077.856,3023.334,3123.553,3162.002,3143.035,3117.522,3004.264,2971.499,2970.035,3091.339,3312.566,3527.791,3700.628,3652.595,3499.127,3347.250,3254.827,3212.112,3157.469,3091.655,3032.771,2982.005,2938.131,2890.961,2839.383,2776.649,2713.609,2655.945,2598.779,2544.316,2485.626,2430.221,2377.389,2333.940,2299.759,2262.659,2357.925,2371.078,2381.128,2403.182,2282.235,2238.074,2193.042,2145.038,2108.918,2075.560,2041.955,2007.901]

energy = [450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600,605,610,615,620,625,630,635,640,645,650,655,660,665,670,675,680,685,690,695,700,705,710,715,720,725,730,735,740,745,750]

#print len(spec)
spec = pad(spec)
maximum = max(spec)
print len(spec), max(spec)

def make_slit(array_in, width):
	size = len(array_in)
	array_out = range(size)
	for val in array_out:
		if (val > size/2 - width/2) and val < (size/2 + width/2):
			array_out[val] = 1
		else:
			array_out[val] = 0
	return array_out

def gauss(x, mu, width):
	return 1 / math.sqrt(2 * math.pi * width**2) * math.exp(-(x - mu)**2 / (2 * width**2))
		
slit = make_slit(spec, 20) # [gauss(x, len(spec)/2, 10) for x in range(len(spec))] # 
plot_slit = Plot("Slit", "pixel", "value")
plot_slit.addPoints("", range(len(slit)), slit, Plot.LINE)
plot_slit.show()
print len(slit), max(slit)

transform = FastFourierTransformer(DftNormalization.STANDARD) # Alternative: DftNormalization.UNITARY
spec_fft = transform.transform(spec, TransformType.FORWARD)
slit_fft = transform.transform(slit, TransformType.FORWARD)

plot_fft = Plot("FFT", "pixel", "value")
plot_fft.addPoints("", range(len(spec_fft)), [x.abs() for x in spec_fft], Plot.LINE)
plot_fft.setColor(Color.RED)
plot_fft.addPoints("", range(len(spec_fft)), [x.getReal() for x in slit_fft], Plot.LINE)
plot_fft.setLimits(float('nan'),float('nan'),float('nan'),float('nan'));
plot_fft.show()

conv_fft = [fft1.multiply(fft2) for fft1, fft2 in zip(spec_fft, slit_fft)]
conv_c = transform.transform(conv_fft, TransformType.INVERSE)
conv = [x.abs() for x in conv_c]
deconv = [fft1.divide(fft2).log() for fft1, fft2 in zip(spec_fft, slit_fft)]
result_c = transform.transform(spec_fft, TransformType.INVERSE)
#print result_c
result = [max(spec)*x.abs() for x in result_c]

plot = Plot("Entfaltung", "Energieverlust [eV]", "Intensity [a.u.]")
plot.addPoints("", energy, result, Plot.LINE)
plot.setColor(Color.RED)
plot.addPoints("", energy, spec, Plot.LINE)
plot.setLimits(float('nan'),float('nan'),float('nan'),float('nan'));
plot.show()