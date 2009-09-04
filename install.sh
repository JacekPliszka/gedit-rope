#!/bin/sh

GEDIT_PLUGINS_PATH="$HOME/.gnome2/gedit/plugins/"
echo "Installing to $GEDIT_PLUGINS_PATH"
cp ropeplugin.gedit-plugin $GEDIT_PLUGINS_PATH
cp -r ropeplugin $GEDIT_PLUGINS_PATH

