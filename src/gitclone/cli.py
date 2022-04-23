import sys

import typer

from click.exceptions import Abort

from gitclone.core import clone as do_clone
from gitclone.utils import print, catch_cli_exception


cli = typer.Typer()


@cli.callback(invoke_without_command=True)
def default():
    pass


@cli.command()
@catch_cli_exception()
def clone(debug: bool = typer.Option(False, "--debug", "-d")):
    do_clone()


def main():
    command = typer.main.get_command(cli)
    try:
        command(standalone_mode=False)
    except (Abort, KeyboardInterrupt):
        print(f"[red][bold]Fatal: [/]Aborted by user...[/]")
        sys.exit(42)


if __name__ == "__main__":
    main()
