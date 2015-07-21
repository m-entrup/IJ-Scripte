input = getDirectory("Input directory");

var array;
var init = true;

processFolder(input);

Dialog.create("Select files");
for (i=0; i<array.length; i++) {
	Dialog.addCheckbox(array[i], true);
}
var array_new;
init = true;
Dialog.show();
for (i=0; i<array.length; i++) {
	if (Dialog.getCheckbox()) {
		if (init) {
			array_new = newArray(1);
			array_new[0] = array[i];
			init = false;
		} else {
			array_new = Array.concat(array_new, array[i]);
		}
	}
}

Array.show("My Array", array_new);

function processFolder(input) {
	list = getFileList(input);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(list[i]))
			processFolder("" + input + list[i]);
		else
			processFile(input, list[i]);
	}
}

function processFile(input, file) {
	if (init) {
		array = newArray(1);
		array[0] = file;
		init = false;
	} else {
		array = Array.concat(array, file);
	}
}
