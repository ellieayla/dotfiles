#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# ]
# ///

import functools
import itertools
import os
from os.path import expanduser
from pathlib import Path
import subprocess

from argparse import ArgumentParser
from collections.abc import Iterable
from typing import Callable, IO, Iterator


class Colors:
    """Minimal piece of stdlib _colorize"""

    RESET = "\x1b[0m"
    BOLD_RED = "\x1b[1;31m"
    BOLD_GREEN = "\x1b[1;32m"
    BOLD_BLUE = "\x1b[1;34m"
    BOLD = "\x1b[1m"

    INTENSE_GREEN = "\x1b[92m"
    GREEN = "\x1b[32m"
    GREY = "\x1b[90m"

    @classmethod
    def disable(cls) -> None:
        for attr in cls.__dict__.keys():
            if not attr.startswith("__"):
                setattr(cls, attr, "")

    @classmethod
    def can(cls, file: "IO[str] | IO[bytes]") -> bool:
        # overrides
        if os.environ.get("NO_COLOR", None):
            return False
        if os.environ.get("FORCE_COLOR", None):
            return True
        if os.environ.get("TERM", None) == "dumb":
            return False

        if not hasattr(file, "fileno"):
            return False

        try:
            return os.isatty(file.fileno())
        except OSError:
            return hasattr(file, "isatty") and file.isatty()


class NoOutput(BaseException):
    """Discard all output from this check, leaving the old output in place."""


class DiscardOldOutput(BaseException):
    """Remove existing .motd file for this check, leaving nothing behind."""

checks = {}

CHECK_FUNCTION = Callable[[], str | Iterable[str]]

def check(func: CHECK_FUNCTION | str) -> CHECK_FUNCTION:
    """Register a check callback."""
    def decorator(func: CHECK_FUNCTION, name: str) -> CHECK_FUNCTION:
        # register the check function by name
        def wrapper():
            """Deferred to runtime - actually call the function."""
            r = func()
            if isinstance(r, str):
                return r.splitlines()
            return r
        if name in checks:
            raise ValueError(f"Duplicate check name {name}")
        checks[name] = wrapper
        return wrapper

    # if passed a callable function, pretend to be and run the decorator function with a constructed name.
    if callable(func):
        return decorator(func, name=func.__name__)

    # if passed a string, return the decorator with the desired name partially populated.
    assert isinstance(func, str)
    return functools.partial(decorator, name=func)


def replace_home(text: str) -> str:
    """Replace any mentions of our home directory with ~, undoing expanduser()."""
    home: str = expanduser("~")
    return text.replace(home, "~")

"""
@check("dotfiles-status")
def dotfiles_status() -> Iterable[str]:
    verify_retcode = subprocess.call(["chezmoi", "verify"])
    if verify_retcode == 1:
        yield "Changes to managed dotfiles: (chezmoi status)"
        yield "chezmoi diff --reverse"
        yield "chezmoi re-add [file]"
        yield "chezmoi re-add --interactive"
        yield "chezmoi apply --interactive"

        files_to_change = subprocess.check_output(["chezmoi", "status", "--path-style", "absolute"], text=True).splitlines()
        for chezmoi_status_row in files_to_change:
            yield f"    {replace_home(chezmoi_status_row)}"
"""

"""
@check("named")
def crapname():
    return "what\neven"
"""

def run_external_check(executable: Path) -> str:
    return subprocess.check_output([executable.as_posix()], text=True).splitlines()


def load_external_checks(from_directory: Path) -> Iterable[Callable]:
    for check_file in from_directory.iterdir():
        if check_file.name.startswith("."):
            # hidden files
            continue

        assert check_file.is_absolute()
        # make a check function that runs the external program
        check_name = check_file.with_suffix("").name
        check_fn = functools.partial(run_external_check, executable=check_file)

        # register it
        check(check_name)(check_fn)


def render_check_output(rows: Iterable[str] | None, name: str | None) -> str:
    if rows is None:
        raise NoOutput

    name_r = f" ({Colors.GREY}{name}{Colors.RESET})" if name else ""
    first_line = next(itertools.islice(rows, 1))

    return "\n".join([
        f"{Colors.BOLD_RED}{first_line}{Colors.RESET}{name_r}"
    ] + [
        f" {Colors.BOLD_BLUE}|{Colors.RESET} {row}" for row in rows
    ])


errors = []

@check
def _errors_while_running_checks():
    if errors:
        yield "Error running some motd generators:"
        yield from errors


def main() -> int:
    p = ArgumentParser(__doc__)

    checks_dir: Path = Path(__file__).parent / "checks"
    load_external_checks(from_directory=checks_dir)
    p.add_argument("--write-state-dir", metavar="D", type=Path, default=Path("~/.local/state/motd").expanduser(), help="Manage .motd files here. (default %(default)s)")
    p.add_argument("--stdout", action="store_true", help="Dump to stdout instead of .motd files.")
    p.add_argument("--run", nargs="+", metavar="fn", choices=list(checks.keys()), help="Run checks (choices: %(choices)s)")
    args = p.parse_args()

    write_state_dir: Path = args.write_state_dir
    if not args.stdout:
        write_state_dir.mkdir(parents=True, exist_ok=True)


    for check_function_name, check_function in sorted(checks.items(), key=lambda _: _[0].startswith("_")):
        if args.run is None or check_function_name in args.run:
            outfile: Path = (write_state_dir / check_function_name).with_suffix(".motd")

            try:
                r = check_function()
                s: str = render_check_output(iter(r), name=check_function_name)

            except DiscardOldOutput:
                # Not only is there no updated output, the old output should be thrown away.
                if not args.stdout:
                    outfile.unlink()
                continue

            except (NoOutput, StopIteration):
                # Presumably check "successfully" returned a zero-length generator/list.
                continue

            except BaseException as e:
                errors.append(str(e))
                continue

            if args.stdout:
                print(s, end="\n\n")

            else:
                # state directory might contain existing .motd files
                # they're going to be overwritten = refreshed here
                # the displayer is responsible for deleting them when viewed
                outfile: Path = (write_state_dir / check_function_name).with_suffix(".motd")
                outfile.write_text(s)


if __name__ == "__main__":
    raise SystemExit(main())
