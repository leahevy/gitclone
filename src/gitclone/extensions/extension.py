from abc import ABC, abstractmethod

from typer import Typer


class Extension(ABC):
    @property
    @abstractmethod
    def command_name(self) -> str:
        ...

    @property
    @abstractmethod
    def command(self) -> Typer:
        ...
