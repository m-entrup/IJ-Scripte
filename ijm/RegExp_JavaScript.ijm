/*
 * file:	RegExp_JavaScript.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20151118
 * info:	Dieses Macro zeigt auf, wie man mit Hilfe von JavaScript per RegExp sucht.
 * 			IJ1 Macro enthält zwar auch eine Funktion zum suchen in RegExp (matches), aber mit dieser kann man nicht auf die gefundenen Gruppen zugreifen.
 * 			Diese fehlende Funktionalität kann man mit Hilfe von JavaScript per 'eval' Funktion nutzen.
 */

name = getString("Bitte Vorname und Nachname eingeben:", "Michael Entrup");
code = "var Ausdruck = /(\\w.+)\\s(\\w.+)/;\n";
code += "Ausdruck.exec('" + name + "');\n";
code += "RegExp.$2 + ', ' + RegExp.$1;";
returned = eval("script", code);
showMessage("Vertauscht", "Vor- und Nachname wurden vertauscht:\n" + returned);