dirIn = getDirectory("Choose Source Directory ");
format = getFormat();
dirOut = getDirectory("Choose Destination Directory ");
setBatchMode(true);
processFolder(dirIn, dirOut);


function processFolder(dir1, dir2) {
	counter = 0;
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
				getPixelSize(unit, pixelWidth, pixelHeight);
				width = getWidth();
				if (unit == "nm")
					barWidth = round(width * pixelWidth / 50) * 10;
				else
					barWidth = round(width * pixelWidth / 0.5) / 10;			
				run("Scale Bar...", "width="+barWidth+" height=10 font=24 color=White background=Black location=[Lower Right] bold");
		 		saveAs(format, dir2+list[i]);
		 		run("8-bit");
		 		if (format == "TIFF")
		 			saveAs("PNG", dir2+list[i]);
		 		close();
		 		counter++;
			}
 		}
	}
	if(counter == 1) 
		str = " file ";
	else
		str = " files ";
	showMessage(counter + str + "converted.");
}

function getFormat() {
   formats = newArray("TIFF", "8-bit TIFF", "JPEG", "GIF", "PNG",
      "BMP", "Text Image", "ZIP", "Raw");
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