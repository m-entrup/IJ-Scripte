/*
 * Dieses Macro zeigt auf, wie man mit Hilfe von JavaScript per RegExp sucht.
 * IJ1 Macro enthält zwar auch eine Funktion zum suchen in RegExp (matches), aber mit dieser kann man nicht auf die gefundenen Gruppen zugreifen.
 * Diese fehlende Funktionalität kann man mit Hilfe von JavaScript per 'eval' Funktion nutzen.
 */

code = "var Ausdruck = /(\\w.+)\\s(\\w.+)/;\n";
code += "Ausdruck.exec('Michael Entrup');\n";
code += "RegExp.$2 + ', ' + RegExp.$1;";
returned = eval("script", code);
IJ.log(returned);