/*
 * file:	RegExp_Jython.ijm
 * author:	Michael Entrup b. Epping (michael.entrup@wwu.de)
 * version:	20151118
 * info:	Dieses Macro zeigt auf, wie man mit Hilfe von Jython per RegExp sucht.
 * 			IJ1 Macro enthält zwar auch eine Funktion zum suchen in RegExp (matches), aber mit dieser kann man nicht auf die gefundenen Gruppen zugreifen.
 * 			Diese fehlende Funktionalität kann man mit Hilfe von Jython per 'eval' Funktion nutzen.
 * 			Anders als bei JavaScript lässt sich das Ergebnis anscheinend nicht als Rückgabewert einfangen.
 * 			Man muss print verwenden, was zu einem Eintrag im Log führt.
 */

name = getString("Bitte Vorname und Nachname eingeben:", "Michael Entrup");
code = "import re\n";
code += "p = re.compile('(\\w.+)\\s(\\w.+)')\n";
code += "m = p.match('" + name + "')\n";
code += "print m.group(2) + ', ' + m.group(1)"
eval("python", code);