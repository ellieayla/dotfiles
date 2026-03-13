#!/usr/bin/env bash

set -uo pipefail

# shellcheck writes - for each file passed on stdin. Replace it with the original filename in $1.
function replace-dash() {
    python3 -c "import sys; import re; filename=sys.argv[1]; [print(_.replace('\x1b[1mIn - line ', '\x1b[1mIn %s line ' % filename), end='') for _ in sys.stdin.readlines()]" $1
}

exitcode=0
for FILE in "$@";
do
    chezmoi execute-template --file "$FILE" | shellcheck -Calways - | replace-dash $FILE
    if [ $? -gt 0 ]; then
        exitcode=1
    fi
done
exit $exitcode
