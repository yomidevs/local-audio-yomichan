#!/usr/bin/env bash

plugin_name=LocalAudioDev
plugin_path_linux=~/.local/share/Anki2/addons21
plugin_path_mac=~/Library/Application\ Support/Anki2/addons21
expanded_mac_path="${plugin_path_mac/#\~/$HOME}"

if [ -d "$plugin_path_linux" ]; then
    ln -s -f $(pwd)/plugin $plugin_path_linux/$plugin_name
fi

if [ -d "$expanded_mac_path" ]; then
    ln -s -f $(pwd)/plugin $expanded_mac_path/$plugin_name
fi
