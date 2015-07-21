/*
 * Ein kleies Macro, welches eine Datei aus dem Internet herunter läd und anschließend auf der Festplatte speichert.
 */

path = getDirectory("Speicherort...");
url = "http://rsbweb.nih.gov/ij/macros/ExecExamples.txt";
open(url);
temp = split(url, "/");
file = temp[temp.length -1];
save(path + file);
run("Close");