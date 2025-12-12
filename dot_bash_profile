
# Use /usr/bin/diff directly for normal style
function diff {
     colordiff -u "$@" | less -RF
}

eval "$(pyenv init -)"

if [ -f ~/.git-completion.bash ]; then
  . ~/.git-completion.bash
fi

export PATH=$PATH:~/bin

export EDITOR="mate"
export KUBE_EDITOR="mate -w"

#https://michael-kuehnel.de/node.js/2015/09/08/using-vm-to-switch-node-versions.html
export NVM_DIR=~/.nvm
# NVM_PRFIX=$(brew --prefix nvm)  # this is really slow
NVM_PREFIX=/usr/local/opt/nvm
source ${NVM_PREFIX}/nvm.sh

GPG_TTY=$(tty)

# https://askubuntu.com/questions/80371/bash-history-handling-with-multiple-terminals
#PROMPT_COMMAND="$PROMPT_COMMAND; history -a; history -r"

# https://unix.stackexchange.com/questions/1288/preserve-bash-history-in-multiple-terminal-windows
HISTCONTROL=ignoredups:erasedups  
shopt -s histappend

# Setting PATH for Python 3.8
# The original version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:${PATH}"
export PATH

export PATH="$HOME/.poetry/bin:$PATH"

# https://coderwall.com/p/-k_93g/mac-os-x-valueerror-unknown-locale-utf-8-in-python
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
. "$HOME/.atuin/bin/env"
