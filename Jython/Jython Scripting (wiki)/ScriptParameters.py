# @Short(label='Image size', value=512) img_size
# @Double(label='Image amplitude', value=1.0) amplitude
# @Short(label='Spacing', value=16) spacing

# The parameters in front of this comment are populated before the script runs.

# The module __future__ contains some useful functions:
# https://docs.python.org/2/library/__future__.html
from __future__ import with_statement, division
import math
from ij import IJ

def split_list(alist, wanted_parts=1):
	"""Split a list to the given number of parts."""
	length = len(alist)
	return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
			 for i in range(wanted_parts) ]

def fft_filter(imp):
	"""Removing noise from an image by using a FFT filter"""
	IJ.run(imp, "FFT", "")
	from ij import WindowManager as wm
	fft = wm.getImage("FFT of " + imp.getTitle())
	IJ.run(fft, "Find Maxima...", "noise=64 output=[Point Selection] exclude")
	# Enlarging the point selectins from Find Maxima.
	IJ.run(fft, "Enlarge...", "enlarge=2")
	# Inverting the selection.
	IJ.run(fft, "Make Inverse", "")
	IJ.run(fft, "Macro...", "code=v=0");
	IJ.run(fft, "Inverse FFT", "")
	fft.changes = False
	fft.close()
	imp_filtered = wm.getImage("Inverse FFT of " + imp.getTitle())
	imp_filtered.setTitle("Filtered " + imp.getTitle())
	imp_filtered.changes = False

# It's best practice to create a function that contains the code that is executed when running the script.
# This enables us to stop the script by just calling return.
def run_script():
	# We can use import inside of code blocks to limit the scope.
	from ij import ImagePlus
	from ij.process import FloatProcessor
	blank = IJ.createImage("Blank", "32-bit black", img_size, img_size, 1)
	# This create a list of lists. Each inner list represents a line.
	# pixel_matrix[0] is the first line where y=0.
	pixel_matrix = split_list(blank.getProcessor().getPixels(), wanted_parts=img_size)
	# This swaps x and y coordinates.
	# http://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python
	# As zip() creates tuples, we have to convert each one by using list().
	pixel_matrix = [list(x) for x in zip(*pixel_matrix)]
	for y in range(img_size):
		for x in range(img_size):
			# This function oszillates between 0 and 1.
			# The distance of 2 maxima in a row/column is given by spacing.
			val = (0.5 * (math.cos(2*math.pi/spacing*x) + math.sin(2*math.pi/spacing*y)))**2
			# When assigning, we multiply the value by the amplitude.
			pixel_matrix[x][y] = amplitude * val
	# The constructor of FloatProcessor works fine with a 2D Python list.
	crystal = ImagePlus("Crystal", FloatProcessor(pixel_matrix))
	crystal_with_noise = crystal.crop()
	crystal_with_noise.setTitle("Crystal with noise")
	IJ.run(crystal_with_noise, "Add Specified Noise...", "standard=%d" % int(amplitude/math.sqrt(2)))
	crystal.show()
	crystal_with_noise.show()
	fft_filter(crystal_with_noise)


# If a Jython script is run, the variable __name__ contains the string '__main__'.
# If a script is loaded as module, __name__ has a different value.
if __name__ == '__main__':
	run_script()