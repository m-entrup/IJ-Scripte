from __future__ import division

import math

from org.apache.commons.math3.fitting import SimpleCurveFitter
#from org.apache.commons.math3.fitting import PolynomialCurveFitter
from org.apache.commons.math3.fitting import WeightedObservedPoints
from org.apache.commons.math3.analysis import ParametricUnivariateFunction

class Zlp(ParametricUnivariateFunction):

	def value(self, x, parameters):
		a, m, s = parameters
		return a * math.exp(-(x - m)**4/(4 * (1.1 * s)**4))

	def gradient(self, x, parameters):
		a, m, s = parameters
		da = math.exp(-(m - x)**4 / (4 * (1.1 * s)**4))
		dm = -(m - x)**3 * self.value(x, parameters) / (1.1 * s)**4
		ds = (m - x)**4 * self.value(x, parameters) / (1.1 * s)**5
		return [da, dm, ds]

def main():
	func = Zlp()
	params = [9.0, 0.1, 1.1]
	params_start = [1.0, 0.0, 1.0]
	fitter = SimpleCurveFitter.create(func, params_start)
	#PolynomialCurveFitter.create(2)
	
	xs = range(-10, 11)
	xs = [x / 10 for x in xs]
	ys = [func.value(x, params) for x in xs]
	dys = [func.gradient(x, params) for x in xs]
	
	points = WeightedObservedPoints()
	for x, y in zip(xs, ys):
		points.add(1, x, y)
	result = fitter.fit(points.toList())
	print(list(result))

if __name__ == '__main__':
	main()