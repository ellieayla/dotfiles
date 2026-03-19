#!/usr/bin/env bash

function indent() {
	awk '{print "\t"$0}'
}

if [ "$(chezmoi unmanaged)" != "" ]; then
	echo "Unmanaged dotfiles: (chezmoi unmanaged)"
	echo "chezmoi add"
	echo "$EDITOR ~/.local/share/chezmoi/.chezmoiignore"
	chezmoi unmanaged --path-style absolute | replace-home | indent
fi
