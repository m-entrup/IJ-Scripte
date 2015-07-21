from ij import IJ
from ij.plugin import Duplicator

# Datei: Weihnachtskarte_2014.py
# Autor: Michael Entrup (michael.entrup@wwu.de)
# Beschreibung: Mit diesem Script kann man das Motiv der Weihnachtskarte unserer Arbeitsgruppe selber erstellen.
#				Man benötigt nur Fiji [1] und schon kann es losgehen:
#				1. Im Menü 'Plugins > New > Macro' auswählen
#				2. Diesen Code in den Editor kopieren
#				3. Im Menü des Editor 'Language > Python' auswählen
#				4. Run ([Strg]+[R]) klicken und warten, bis das Bild fertig ist 
#
# [1]: http://imagej.net/Fiji

# Es dürfen keine Bilder offen sein, da später ein Stack erstellt wird.
if IJ.showMessageWithCancel("Warnung!", "Alle geoeffneten Bilder werden geschlossen!\nOK um fortzufahren."):
	IJ.run("Close All", "")
	
	# FFT erzeugen und optimieren:
	# Das ursprüngliche wird aus dem Internet geladen.
	imp = IJ.openImage("http://uni.entrup.com.de/Fe_Cr_SiO_Si.tif")
	# Nur unten rechts gibt es reines Silizium.
	imp.setRoi(2430, 2430, 1666, 1666)
	IJ.run(imp, "FFT", "")
	fft = IJ.getImage()
	IJ.run(fft, "Smooth", "")
	# Durch die Exponentialfunktion sind die Spots besser sichtbar.
	IJ.run(fft, "Exp", "")
	IJ.run(fft, "Enhance Contrast", "saturated=0.35")
	
	# Rotieren und skalieren der FFT:
	# Es werden 35 neue Bilder erzeugt.
	for arc in range(10,360,10):
		scale = 1.0
		if (arc % 60 == 10): scale = 0.8
		if (arc % 60 == 20): scale = 0.6
		if (arc % 60 == 30): scale = 0.4
		if (arc % 60 == 40): scale = 0.6
		if (arc % 60 == 50): scale = 0.8
		duplicator = Duplicator()
		temp = duplicator.run(fft)
		IJ.run(temp, "Scale...", "x=" + str(scale) + " y=" + str(scale) + " interpolation=Bicubic average")
		IJ.run(temp, "Rotate... ", "angle=" + str(arc) + " grid=1 interpolation=Bicubic")
		temp.show()
	
	# Projektion aller 36 FFTs erstellen:
	# Alle offenen Bilder werden zu einem Stack zusammengefügt.
	# Deshalb müssen am Anfang alle anderen BIlder geschlossen werden.
	IJ.run("Images to Stack", "")
	stack = IJ.getImage()
	stack.show()
	IJ.run(stack, "Z Project...", "projection=[Max Intensity]")
	IJ.run(IJ.getImage(), "Enhance Contrast", "saturated=0.35")
	# Es wird nicht das vollständige Bild benötigt.
	motiv = IJ.getImage()
	motiv.setRoi(384, 384, 1280, 1280)
	IJ.run(motiv, "Crop", "")
	# In der oberen, linken Ecke wird ein Rahmen für das Overlay erstellt.
	motiv.setRoi(1, 1, 343, 343)
	IJ.run(motiv, "Draw", "")
	motiv.setRoi(0, 0, 345, 345)
	IJ.run(motiv, "Draw", "")
	IJ.run(motiv, "Select None", "")
	
	# Overlay hinzufügen:
	IJ.run(stack, "Duplicate...", " ")
	small = IJ.getImage()
	IJ.run(small, "Bin...", "x=6 y=6 bin=Average")
	IJ.selectWindow(motiv.getTitle())
	IJ.run("Add Image...", "image=["+ small.getTitle() +"] x=2 y=2 opacity=100")

	# Temporäre Bilder schließen:
	small.close()
	stack.close()

	# Am Ende benötigt das Bild noch einen passenden Namen:
	motiv.setTitle("Weihnachtskarte 2014")
else:
	IJ.showStatus("Script wurde abgebrochen.")