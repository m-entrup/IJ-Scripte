from __future__ import division
import math
from org.apache.commons.math3.complex import Complex
from org.apache.commons.math3.transform import FastFourierTransformer, DftNormalization, TransformType


transform = FastFourierTransformer(DftNormalization.STANDARD)

def fft(array):
	return transform.transform(array, TransformType.FORWARD)

def ifft(array):
	return transform.transform(array, TransformType.INVERSE)

print fft([1,1,1,1])
print fft([1,1,1,1,1,1,1,1])
print fft([1,-1,1,-1])
print fft([1,-1,1,-1,1,-1,1,-1])

print ifft(fft([1,-1,1,-1]))


transform = FastFourierTransformer(DftNormalization.UNITARY)

print fft([1,1,1,1])
print fft([1,1,1,1,1,1,1,1])
print fft([1,-1,1,-1])
print fft([1,-1,1,-1,1,-1,1,-1])

print ifft(fft([1,-1,1,-1]))