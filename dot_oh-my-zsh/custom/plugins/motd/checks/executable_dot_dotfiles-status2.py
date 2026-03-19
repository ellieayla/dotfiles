#!/usr/bin/env python3

if __name__ == "__main__":
    verify_retcode = subprocess.call(["chezmoi", "verify"])
    if verify_retcode == 1:
        print(f" {Colors.BOLD_BLUE}->{Colors.RESET} chezmoi diff --reverse")
        print(f" {Colors.BOLD_RED}Changes to managed dotfiles: (chezmoi status){Colors.RESET}")
        print(f" {Colors.BOLD_BLUE}->{Colors.RESET} chezmoi re-add [file]")
        print(f" {Colors.BOLD_BLUE}->{Colors.RESET} chezmoi re-add --interactive")
        print(f" {Colors.BOLD_BLUE}->{Colors.RESET} chezmoi apply --interactive")
	    #chezmoi status --path-style absolute | replace-home | indent"
