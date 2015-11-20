#!/bin/bash

# file: syncWithFiji.sh
# version: 20151120
# info: Synchronisiert Macros, Scripte und Plugins mit Fiji.

WD=$(dirname $0)
FIJI=$HOME/Software/Fiji.app
MACROS=$FIJI/macros/Eigene
PLUGINS=$FIJI/plugins/Eigene

echo -e "\nLösche archivierte Dateien aus Fiji..."
for file in $WD/Archiv/*
do
	filePath=$MACROS/$(basename $file)
	if [ -f $filePath ]
	then
		rm -v $filePath
	fi
	filePath=$PLUGINS/$(basename $file)
	if [ -f $filePath ]
	then
		rm -v $filePath
	fi
done

# Möchte man mit rsync nur bestimmte Dateien kopieren und Unterordner einschließen, dann wird es etwas komplizierter:
# mit --include wählt man Dateien nach einem Pattern aus. Leider werden auch alle weiteren Dateien ausgewählt, wenn man sie nicht explizit ausschließt.
# --exclude "*" schließt jedoch auch alle Verzeichnisse aus und eine Rekursion wird nicht durchgeführt.
# Als alternative lässt sich --filter "-! */" verwenden, das alle Dateien ausschließt, außer die per --include gewählten.
# Gefunden habe ich diesen Tipp auf [1].
#
# [1] http://blog.mudflatsoftware.com/blog/2012/10/31/tricks-with-rsync-filter-rules/
echo -e "\nSynchronisiere Java-Plugins..."
rsync -avzhu --include "*.jar" --include "*.class" --filter "-! */" --prune-empty-dirs $WD/java/ $PLUGINS/
rsync -avzhu --include "*.jar" --include "*.class" --filter "-! */" --prune-empty-dirs $PLUGINS/ $WD/java/

echo -e "\nSynchronisiere IJ-Macros..."
rsync -avzhu  --include "*.ijm" --filter "-! */" --prune-empty-dirs $WD/ijm/ $MACROS/
rsync -avzhu  --include "*.ijm" --filter "-! */" --prune-empty-dirs $MACROS/ $WD/ijm/

echo -e "\nSynchronisiere JavaScript..."
rsync -avzhu  --include "*.js" --filter "-! */" --prune-empty-dirs $WD/js/ $MACROS/
rsync -avzhu  --include "*.js" --filter "-! */" --prune-empty-dirs $MACROS/ $WD/js/

echo -e "\nSynchronisiere Jython..."
rsync -avzhu --include "*.py" --filter "-! */" --prune-empty-dirs $WD/Jython/ $MACROS/
rsync -avzhu --include "*.py" --filter "-! */" --prune-empty-dirs $MACROS/ $WD/Jython/

exit 0
