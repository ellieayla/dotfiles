#!/usr/bin/env bash

function indent() {
	awk '{print "\t"$0}'
}

chezmoi verify
if [ "$?" -ne 0 ]; then
	# not all target home directory files match the source repo
	echo "Changes to managed dotfiles: (chezmoi status)"
	echo "chezmoi diff --reverse"
	echo "chezmoi re-add [file]"
	echo "chezmoi re-add --interactive"
	echo "chezmoi apply --interactive"
	chezmoi status --path-style absolute | replace-home | indent
fi
