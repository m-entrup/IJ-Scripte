/*
 * file:	Batch_Converter.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20151117
 * info:	Das Macro konvertiert Dateien mit den in formats hinterlegten Endungen.
 * 			Alle unterordner werden bei der Suche nach geeigneten Dateien einbezogen.
 * 			Das Format der erzeugten Dateien lässt sich mit Hilfe eines Dialog auswählen.
 */

formats = newArray("TIFF", "8-bit TIFF", "JPEG", "GIF", "PNG", "BMP", "Text Image", "ZIP", "Raw");

dirIn = getDirectory("Choose Source Directory ");
format = getFormat();
dirOut = getDirectory("Choose Destination Directory ");
setBatchMode(true);
counter = 0
processFolder(dirIn, dirOut);
if(counter == 1)
	str = " file ";
else
	str = " files ";
showMessage(counter + str + "converted.");


function processFolder(dir1, dir2) {
	list = getFileList(dir1);
	for (i=0; i<list.length; i++) {
		if(File.isDirectory(dir1+list[i]))
		 	processFolder(dir1 + list[i] + File.separator, dir2 + list[i] + File.separator);
		else {
			if (checkFileType(list[i])) {
				open(dir1+list[i]);
		 		if (format=="8-bit TIFF" || format=="GIF")
		    		convertTo8Bit();
		    	if (!File.exists(dir2))
		    		File.makeDirectory(dir2);
				run("Enhance Contrast", "saturated=0.35");
		 		saveAs(format, dir2+list[i]);
		 		close();
		 		counter++;
			}
 		}
	}
}

function getFormat() {
   Dialog.create("Batch Convert");
   Dialog.addChoice("Convert to: ", formats, "TIFF");
   Dialog.show();
   return Dialog.getChoice();
}

function checkFileType(file) {
	formats = newArray("tif", "tiff", "jpg", "jpeg", "gif", "png", "bmp", "dm3");
	for (i = 0; i < formats.length; i++) {
		if (endsWith(toLowerCase(file), "." + formats[i]))
			return true;
	}
	return false;
}

function convertTo8Bit() {
  if (bitDepth==24)
      run("8-bit Color", "number=256");
  else
      run("8-bit");
}