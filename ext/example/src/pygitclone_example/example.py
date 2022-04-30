import sys

from typer import Typer

from gitclone.extensions import Extension
from gitclone.utils import print

cli = Typer()


@cli.callback(invoke_without_command=True)
def default(name: str) -> None:
    print(f"[green]Hello world from example extension:[/] [yellow]{name}[/]")


class ExampleExtension(Extension):
    def __init__(self) -> None:
        print("Running some extension init code...", file=sys.stderr)

    @property
    def command_name(self) -> str:
        return "example"

    @property
    def command(self) -> Typer:
        return cli


__all__ = ["ExampleExtension"]
