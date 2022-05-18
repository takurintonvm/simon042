#!/bin/sh

POT=gnome-shell-extension-weather.pot 
TMP=messages.po
TMP2=messages2.po

echo '' > $TMP
pushd ../src
xgettext -o ../po/$TMP -L python -j --keyword=_ extension.js
popd
msgmerge -N $POT $TMP > $TMP2
mv $TMP2 $POT
rm -f $TMP $TMP2
