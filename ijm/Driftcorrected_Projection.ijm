/*
 * file:	Driftcorrected_Projection.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20151117
 * info:	Das Macro läd eine Bildserie und führt eine Driftkorrektur durch.
 * 			Zur Driftkorrektur wird Linear Stack Alignment with SIFT verwendet.
 * 			Anschließend wird eine Projektion mit der gewählten Metode ausgeführt.
 */


main();


function main() {
	var paras = getParameters();
	var contains = paras[0];
	var projectionMethod = paras[1];
	setBatchMode(true);
	run("Image Sequence...", "open=[file=" + contains + " sort");
	var initialStack = getImageID();
	var title = getTitle();
	var width, height, depth, unit;
	getVoxelSize(width, height, depth, unit);
	run("Linear Stack Alignment with SIFT", "initial_gaussian_blur=1.60 steps_per_scale_octave=3 minimum_image_size=64 maximum_image_size=1024 feature_descriptor_size=4 feature_descriptor_orientation_bins=8 closest/next_closest_ratio=0.92 maximal_alignment_error=25 inlier_ratio=0.05 expected_transformation=Translation interpolate");
	var correctedStack = getImageID();
	run("Z Project...", "projection=[" + projectionMethod + "]");
	var projection = getImageID();
	setVoxelSize(width, height, depth, unit);
	makeRectangle(getWidth/4, getHeight/4, getWidth/2, getHeight/2);
	run("Enhance Contrast", "saturated=0.35");
	run("Select None");
	selectImage(initialStack);
	close();
	selectImage(correctedStack);
	close();
	selectImage(projection);
	rename("[" + projectionMethod + "] " + title);
	setBatchMode("exit and display");
}


function getParameters() {
	Dialog.create("Parameters for driftcrrected Projection");
	Dialog.addString("Filter file name by", "");
	Dialog.addChoice("Method for projection", newArray("Sum Slices", "Average Intensity", "Median", "Standard Deviation"));
	Dialog.show();
	var paras = newArray(2);
	paras[0] = Dialog.getString();
	paras[1] = Dialog.getChoice();
	return paras;
}