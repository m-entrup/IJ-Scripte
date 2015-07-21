/*
 * Dieses Macro zeigt auf, wie man mit Hilfe von Jython per RegExp sucht.
 * IJ1 Macro enthält zwar auch eine Funktion zum suchen in RegExp (matches), aber mit dieser kann man nicht auf die gefundenen Gruppen zugreifen.
 * Diese fehlende Funktionalität kann man mit Hilfe von Jython per 'eval' Funktion nutzen.
 */

code = "import re\n";
code += "p = re.compile('(\\w.+)\\s(\\w.+)')\n";
code += "m = p.match('Michael Entrup')\n";
code += "print m.group(2) + ', ' + m.group(1)"
returned = eval("python", code);
IJ.log(returned);