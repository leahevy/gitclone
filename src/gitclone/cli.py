import functools
import sys
import os.path
import traceback

from click import UsageError

import typer

from click.exceptions import Abort, NoSuchOption, BadArgumentUsage, UsageError

from gitclone.core import clone_from_config, clone_single
from gitclone.utils import print
from gitclone.version import __VERSION__


DEFAULT_COMMAND = []
COMMANDS = []
VERBOSE_HELP = "Print more log messages during run"
DEBUG_HELP = "Run in debug mode (print exceptions)"
VERSION_HELP = "Print the version and exit"

cli = typer.Typer()
state = {"verbose": False, "debug": False}


def command():
    def decorator(f):
        @functools.wraps(f)
        def inner_cmd(*args, verbose=None, debug=None, version=None, **kwargs):
            update_state(verbose=verbose, debug=debug)
            if state["verbose"]:
                print(f"Command {f.__name__}, Args: " + str(sys.argv[1:]))

            if version:
                print(f"v{__VERSION__}")
                sys.exit(0)
            f(*args, verbose=verbose, debug=debug, **kwargs)

        COMMANDS.append(f.__name__)

        inner_cmd = cli.command()(inner_cmd)

        return inner_cmd

    return decorator


def default_command():
    def decorator(f):
        if DEFAULT_COMMAND:
            raise ValueError("There is already a default command")
        DEFAULT_COMMAND.append(f.__name__)
        return f

    return decorator


@command()
def pull(
    verbose: bool = typer.Option(None, "--verbose", "-v", help=VERBOSE_HELP),
    debug: bool = typer.Option(None, "--debug", "-d", help=DEBUG_HELP),
    version: bool = typer.Option(None, "--version", help=VERSION_HELP),
):
    raise ValueError("pull not implemented")


@command()
@default_command()
def clone(
    repository: str = typer.Argument(
        None,
        metavar="<repository>",
        help="Repository for the 'git clone' command",
    ),
    directory: str = typer.Argument(
        None,
        metavar="<directory>",
        help="Directory for the 'git clone' command",
    ),
    verbose: bool = typer.Option(None, "--verbose", "-v", help=VERBOSE_HELP),
    debug: bool = typer.Option(None, "--debug", "-d", help=DEBUG_HELP),
    version: bool = typer.Option(None, "--version", help=VERSION_HELP),
):
    if repository:
        clone_single((repository, directory), verbose=verbose, debug=debug)
    else:
        clone_from_config(verbose=verbose, debug=debug)


@cli.callback()
def typer_main(
    verbose: bool = typer.Option(None, "--verbose", "-v", help=VERBOSE_HELP),
    debug: bool = typer.Option(None, "--debug", "-d", help=DEBUG_HELP),
    version: bool = typer.Option(None, "--version", help=VERSION_HELP),
):
    update_state(verbose=verbose, debug=debug)


def update_state(verbose=None, debug=None):
    if verbose is not None:
        state["verbose"] = verbose
    if debug is not None:
        state["debug"] = debug


def main():
    only_options = True
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and not arg.startswith("-"):
            only_options = False
            break
    if only_options and DEFAULT_COMMAND:
        sys.argv = [sys.argv[0]] + DEFAULT_COMMAND + sys.argv[1:]
    for idx, arg in enumerate(sys.argv):
        if arg == "-h":
            sys.argv[idx] = "--help"
    command = typer.main.get_command(cli)
    try:
        command(standalone_mode=False)
    except (Abort, KeyboardInterrupt) as e:
        if state["debug"]:
            print(traceback.format_exc())
        print(f"[red][bold]Gitclone fatal: [/]Aborted by user...[/]")
        sys.exit(42)
    except (NoSuchOption, BadArgumentUsage, UsageError) as e:
        if state["debug"]:
            print(traceback.format_exc())
        print(f"[red][bold]Gitclone fatal: [/]{str(e)}[/]")
        command_found = False
        for idx, arg in enumerate(sys.argv[1:][:]):
            if arg in COMMANDS:
                command_found = True
                sys.argv = sys.argv[: idx + 2]
                break
            elif not arg.startswith("-"):
                sys.argv = sys.argv[:1]
        if not command_found:
            sys.argv = sys.argv[:1]

        sys.argv = list(filter(lambda arg: not arg.startswith("-"), sys.argv))
        sys.argv += ["--help"]
        print(
            f"  [yellow]Try: "
            + " ".join(
                [os.path.basename(sys.argv[0])] + [f'"{arg}"' for arg in sys.argv[1:]]
            )
            + "[/]"
        )
        sys.exit(43)
    except Exception as e:
        if state["debug"]:
            print(traceback.format_exc())
        print(f"[red][bold]Gitclone fatal: [/]{str(e)}[/]")
        sys.exit(44)

    sys.exit(0)


if __name__ == "__main__":
    main()
