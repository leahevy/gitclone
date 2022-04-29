import functools
import os.path
import sys
import traceback
from typing import Any, Callable

import typer
from click import Command
from click.exceptions import Abort, BadArgumentUsage, NoSuchOption, UsageError

from gitclone.core import GitcloneCore
from gitclone.repositories import RepoSpecification
from gitclone.utils import print
from gitclone.version import __VERSION__

DEFAULT_COMMAND: list[str] = []
COMMANDS: list[str] = []
VERBOSE_HELP = "Print more log messages during run"
DEBUG_HELP = "Run in debug mode (print exceptions)"
VERSION_HELP = "Print the version and exit"
DRY_RUN_HELP = "Don't execute anything"

cli = typer.Typer()
state = {"verbose": False, "debug": False}


def command():  # type: ignore
    def decorator(f):  # type: ignore
        @functools.wraps(f)  # type: ignore
        def inner_cmd(
            *args: list[Any],
            verbose: bool | None = None,
            debug: bool | None = None,
            version: bool | None = None,
            **kwargs: dict[str, Any],
        ) -> None:
            update_state(verbose=verbose, debug=debug)
            if version:
                print(f"v{__VERSION__}")
                sys.exit(0)
            f(*args, verbose=state["verbose"], debug=state["debug"], **kwargs)

        COMMANDS.append(f.__name__)  # type: ignore

        inner_cmd = cli.command()(inner_cmd)  # type: ignore

        return inner_cmd

    return decorator  # type: ignore


def default_command():  # type: ignore
    def decorator(f: Callable[..., None]) -> Callable[..., None]:
        if DEFAULT_COMMAND:
            raise ValueError("There is already a default command")
        DEFAULT_COMMAND.append(f.__name__)
        return f

    return decorator


@command()  # type: ignore
def pull(
    verbose: bool = typer.Option(None, "--verbose", "-v", help=VERBOSE_HELP),
    debug: bool = typer.Option(None, "--debug", "-d", help=DEBUG_HELP),
    version: bool = typer.Option(None, "--version", help=VERSION_HELP),
    dry_run: bool = typer.Option(None, "--dry-run", "-n", help=DRY_RUN_HELP),
) -> None:
    raise ValueError("pull not implemented")


@command()  # type: ignore
@default_command()  # type: ignore
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
    dry_run: bool = typer.Option(None, "--dry-run", "-n", help=DRY_RUN_HELP),
) -> None:
    repos: list[RepoSpecification] = []
    if repository:
        repos.append(RepoSpecification(url=repository, dest=directory))
    core = GitcloneCore(verbose=verbose)
    core.clone(verbose=verbose, dry_run=dry_run)


@cli.callback()
def typer_main(
    verbose: bool = typer.Option(None, "--verbose", "-v", help=VERBOSE_HELP),
    debug: bool = typer.Option(None, "--debug", "-d", help=DEBUG_HELP),
    version: bool = typer.Option(None, "--version", help=VERSION_HELP),
) -> None:
    update_state(verbose=verbose, debug=debug)


def update_state(
    verbose: bool | None = None, debug: bool | None = None
) -> None:
    if verbose is not None:
        state["verbose"] = verbose
    if debug is not None:
        state["debug"] = debug


def main() -> None:
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
    run_command(command)


def run_command(cmd: Command) -> None:
    try:
        cmd(standalone_mode=False)
    except (Abort, KeyboardInterrupt):
        if state["debug"]:
            print(traceback.format_exc())
        print("[red][bold]Gitclone fatal: [/]Aborted by user...[/]")
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
            "  [yellow]Try: "
            + " ".join(
                [os.path.basename(sys.argv[0])]
                + [f'"{arg}"' for arg in sys.argv[1:]]
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
