/*
 * file:	Download_Save.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20151117
 * info:	Ein kleies Macro, welches eine Datei aus dem Internet herunter läd.
 * 			Anschließend wird die Datei auf der Festplatte gespeichert.
 */


url = getString("Url zur Datei:", "http://rsbweb.nih.gov/ij/macros/ExecExamples.txt");
setBatchMode(true);
open(url);
path = getDirectory("Speicherort...");
temp = split(url, "/");
file = temp[temp.length -1];
save(path + file);
run("Close");