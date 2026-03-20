
function motd() {
    emulate -L zsh

    # fast return if MOTD_SKIP set to anything.
    if [[ -n "$MOTD_SKIP" ]]; then
        return 0
    fi
    setopt local_options no_xtrace

    local STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/motd"
    mkdir -p "$STATE_DIR"

    local recent_checkfile="$STATE_DIR/last-motd-display.check"
    touch "$recent_checkfile"

    # self-destructing motd files
    find "$STATE_DIR" -type f -name '*.motd' -exec cat '{}' \; -execdir echo \; -execdir echo \; -delete
}

function motd_display_auto() {
    emulate -L zsh

    # fast return if MOTD_SKIP set to anything.
    if [[ -n "$MOTD_SKIP" ]]; then
        return 0
    fi

    setopt local_options no_xtrace

    local STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/motd"
    mkdir -p "$STATE_DIR"

    # don't be annoying
    local recent_checkfile="$STATE_DIR/last-motd-display.check"
    local MINUTES=10
    if [ -e "$recent_checkfile" ]; then
        if ! find "$recent_checkfile" -type f -mmin +$MINUTES | grep --quiet .; then
            # "recently motd in last $MINUTES minutes, just exit"
            return 0
        fi
    fi

    motd
}
