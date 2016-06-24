"""
file:		Correct_drift.py
author:		Michael Entrup b. Epping (michael.entrup@wwu.de)
version:	20160624
info:		A script that corrects the drift between two images.
			The images are not changed. A copy of the second image is shifted.
			The CrossCorrelation used for drift detection is displayed.
"""

from sys import modules, path
# When using own modules it is necessary to use 'sys.modules.clear()'.
# https://groups.google.com/forum/#!msg/fiji-devel/2YshfLDHiIY/MR0LoRJ6tm4J
# https://stackoverflow.com/questions/10531920/jython-import-or-reload-dynamically
modules.clear()
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/plugins/Scripts/Plugins/EFTEMj/')
import CorrectDrift as drift

drift.correct_drift_gui()