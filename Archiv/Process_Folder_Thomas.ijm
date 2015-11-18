/*
 * Dieses Macro habe ich zusammen mit Thomas erstellt.
 * Es erstellt eine plt-Datei für Gnuplot, die drei Graphen plottet.
 * Die Datensätze für die Graphen werden aus eine Ordnerstruktur herausgesucht.
 * In einem Dialog werden die benötigten Parameter an das Macro übergeben.
 * 
 * Version: 20150115
 */

input = getDirectory("Input directory");
output = "F:\\Plots\\";

Dialog.create("Set filter");
Dialog.addMessage("Verteilung 1:");
Dialog.addChoice("Intensität: ", newArray("Erhöht", "Veringert"));
Dialog.addChoice("Bild: ", newArray("1","2","3", "Alle"));
Dialog.addChoice("Fehler Stärke: ", newArray("5","10","15","20","30","40","50"));
Dialog.addChoice("Fehler Größe: ", newArray("5","10","15","20","30","40","50"));
Dialog.addMessage("Verteilung 2:");
Dialog.addChoice("Intensität: ", newArray("Erhöht", "Veringert"));
Dialog.addChoice("Bild: ", newArray("1","2","3", "Alle"));
Dialog.addChoice("Fehler Stärke: ", newArray("5","10","15","20","30","40","50"));
Dialog.addChoice("Fehler Größe: ", newArray("5","10","15","20","30","40","50"));
Dialog.addMessage("Verteilung 3:");
Dialog.addChoice("Intensität: ", newArray("Erhöht", "Veringert"));
Dialog.addChoice("Bild: ", newArray("1","2","3", "Alle"));
Dialog.addChoice("Fehler Stärke: ", newArray("5","10","15","20","30","40","50"));
Dialog.addChoice("Fehler Größe: ", newArray("5","10","15","20","30","40","50"));
Dialog.show();

int1 = Dialog.getChoice();
bild1 = Dialog.getChoice();
strength1 = Dialog.getChoice();
size1 = Dialog.getChoice();
if (strength1 == size1) strength1 = "Gleich";

int2 = Dialog.getChoice();
bild2 = Dialog.getChoice();
strength2 = Dialog.getChoice();
size2 = Dialog.getChoice();
if (strength2 == size2) strength2 = "Gleich";

int3 = Dialog.getChoice();
bild3 = Dialog.getChoice();
strength3 = Dialog.getChoice();
size3 = Dialog.getChoice();
if (strength3 == size3) strength3 = "Gleich";

var found = newArray();

path1 = processFolder(int1, bild1, strength1, size1);
path2 = processFolder(int2, bild2, strength2, size2);
path3 = processFolder(int3, bild3, strength3, size3);

editCSV(path1);
editCSV(path2);
editCSV(path3);

createPLT(int1+bild1+strength1+size1, path1, int2+bild2+strength2+size2, path2, int3+bild3+strength3+size3, path3);

function processFolder(int, bild, strength, size) {
	path = input;
	list = getFileList(input);
	i = 0;
	while (!matches("" + list[i], ".+" + int + ".+")) {	
		i++;
	}
	path = input + list[i];
	list = getFileList(path);
	if (lengthOf(bild) == 2) {
		case = ".+" + bild + "/";
	} else {
		case = "^" + bild + ".+";
	}
	i = 0;
	print(bild);
	while (!matches("" + list[i], case)) {
		i++;
	}
	path += list[i];
	list = getFileList(path);
	i = 0;
	while (!matches("" + list[i], "\\D+" + strength + "\\D*")) {
		i++;
	}
	path += list[i];
	list = getFileList(path);
	i = 0;
	while (!matches("" + list[i], "\\D*" + size + "\\D+")) {
		i++;
	}
	path += list[i];
	return path;
}

function editCSV(path) {
	if (File.exists(path + "Results_norm.csv")) File.delete(path + "Results_norm.csv");
	run("Clear Results");
	open(path + "Results.csv");
	stepSize = getResult("Value", 2) - getResult("Value", 1);
	sum = 1024*1024;
	for (i=0; i < nResults; i++) {
		norm = getResult("Count", i) / sum / stepSize;
		setResult("Norm", i, norm);	
	}
	run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file");
	saveAs("Results", path + "Results_norm.csv");
}

function createPLT(str1, path1, str2, path2, str3, path3) {
	pltFile = output + str1 + "_" + str2 + "_" + str3 + ".plt";
	if (File.exists(pltFile)) File.delete(output + str1 + "_" + str2 + "_" + str3 + ".plt");
	f = File.open(pltFile);
	print(f, "set xlabel 'Chi^2'");
	print(f, "set ylabel ''");
	print(f, "set xrange[0:8]");
	print(f, "set yrange[0:0.1]");
	print(f, "set terminal pngcairo size 800,600 enhanced");
	print(f, "set output 'chiSquarePlot_" + str1 + "_" + str2 + "_" + str3 + ".png'");
	print(f, "set style data lines");
	print(f, "set grid");
	print(f, "set title '"+ str1 + " " + str2 + " " + str3 + "'");
	print(f, "f(x) = 1./(x*sqrt(2.*pi))*exp(-x/2.)");
	print(f, "plot '" + path1 + "Results_norm.csv' using 1:3 '%lf,%lf,%lf' title '" + str1 + "',\\");
	print(f, "'" + path2 + "Results_norm.csv' using 1:3 '%lf,%lf,%lf' title '" + str2 + "',\\");
	print(f, "'" + path3 + "Results_norm.csv' using 1:3 '%lf,%lf,%lf' title '" + str3 + "',\\");
	print(f, "f(x) notitle");
	print(f, "unset output");
	File.close(f);
}