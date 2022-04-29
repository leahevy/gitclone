from typer import Typer

from gitclone.extensions import Extension
from gitclone.utils import print

cli = Typer()


@cli.callback(invoke_without_command=True)
def default(name: str) -> None:
    print(f"[green]Hello world from example extension:[/] [yellow]{name}[/]")


class ExampleExtension(Extension):
    @property
    def command_name(self) -> str:
        return "example"

    @property
    def command(self) -> Typer:
        return cli
