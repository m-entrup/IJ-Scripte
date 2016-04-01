/*
 * file:	NormStack.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20160329
 * info:	Dieses Script normiert alle Bilder eines Stacks auf den Mittelwert 1.
 * 			Der alte Mittelwert wird als Slice-Label gespeichert, falls der Nutzer dies möchte.
 */
 

isSetSliceLabels = false;
if ( getBoolean("Include means as slice labels?") ) {
	isSetSliceLabels = true;
}
title = getTitle();
run("Duplicate...", "title=" + title + "-norm duplicate");
for (i = 1; i <= nSlices; i++) {
	setSlice(i);
	getStatistics(area, mean, min, max, std, histogram);
	run("Divide...", "value=" + mean + " slice");
	if ( isSetSliceLabels ) {
		run("Set Label...", "label=" + mean);
	}
}
setSlice(1);
run("Enhance Contrast", "saturated=0.35");