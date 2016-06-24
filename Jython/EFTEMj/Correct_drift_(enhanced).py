"""
file:		Correct_drift_(enhanced).py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160624
info:		A script that corrects the drift between any number of images.
			The images are not changed. A stack is created that holds the corrected images.
"""

from __future__ import with_statement, division
from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CrossCorrelation as CC
import HelperDialogs as dialogs

import operator, copy
from ij import IJ, WindowManager

def get_drift(i, j, images):
	cc_img = CC.perform_correlation(images[i], images[j])
	offset = CC.get_shift(cc_img)
	# Mark the image as unchanged to close it without query
	cc_img.changes = False
	cc_img.close()
	""" DEBUG
	print 'Reference: %s at index %i' % (images[i],i)
	print 'Drifted image: %s at index %i' % (images[j],j)
	print 'Offset: %d,%d\n' % offset
	"""
	return offset

def mean_of_list_of_pairs(list):
	x, y = zip(*list)
	return (sum(x)/len(x), sum(y)/len(y))

def main():
	img_count = IJ.getNumber("How many images do you want to correct?", 3)
	# If canceld IJ.getNumber() returns -Integer.MAX_VALUE
	if img_count < 3:
		return False
	image_ids = WindowManager.getIDList()
	image_titles = [WindowManager.getImage(id).getTitle() for id in image_ids]
	images_selected = dialogs.create_selection_dialog(image_titles, range(img_count), 'Select images for drift correction')
	# dialogs.create_selection_dialog() returns None if canceled
	if not images_selected:
		return False
	images = [WindowManager.getImage(image_ids[selection]) for selection in images_selected]
	drift_matrix = [[]] * len(images)
	for i in range(len(images)):
		drift_matrix[i] = [[]] * len(images)
		# print  'i=%i: ' % i, range(i + 1, len(images))
		for j in range(i + 1, len(images)):
			shift = get_drift(i, j, images)
			""" DEBUG
			print 'Appending to %i/%i:' % (i, j)
			print shift
			"""
			drift_matrix[i][j] = [shift]
	print drift_matrix
	i_start = len(images) - 3
	while i_start >= 0:
		drift_matrix_updated = copy.deepcopy(drift_matrix)
		for i in range(i_start, -1, -1):
			for j in range(len(images)-1, 1, -1):
				if j > (i+1):
					""" INFO
					Her is an example for the combination of zip() and asterisk:
					list_of_pairs = [(1,4), (2,5), (3,6)]
					*list_of_pairs -> (1,4), (2,5), (3,6)
					zip(*zipped_list) -> [(1, 2, 3), (4, 5, 6)]
					"""
					x1, y1 = zip(*drift_matrix[i+1][j])
					x2, y2 = zip(*drift_matrix[i][j-1])
					combined = (sum(x1)/len(x1) + sum(x2)/len(x2), sum(y1)/len(y1) + sum(y2)/len(y2))
					drift_matrix_updated[i][j].append(combined)
		drift_matrix = drift_matrix_updated
		print drift_matrix
		i_start -= 1
	print 'Final drif vector: ', map(mean_of_list_of_pairs, drift_matrix[0][1:])
	
main()