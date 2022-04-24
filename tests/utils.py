import os
import os.path
import tempfile
import textwrap
from contextlib import contextmanager
from typing import Generator, TextIO


@contextmanager
def cwd(path: str) -> Generator[None, None, None]:
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        _, tail_path = os.path.splitdrive(os.path.normpath(os.getcwd()))
        separated_path = [p for p in tail_path.split(os.path.sep) if p]
        assert len(separated_path) > 1
        yield
    finally:
        os.chdir(oldpwd)


@contextmanager
def tempdir() -> Generator[None, None, None]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            yield


@contextmanager
def coreconfig() -> Generator[TextIO, None, None]:
    with tempdir():
        with open("gitclone.yaml", "w+") as f:
            yield f


@contextmanager
def textconfig() -> Generator[TextIO, None, None]:
    with tempdir():
        with open("gitclone.txt", "w+") as f:
            yield f


def write(f: TextIO, s: str) -> None:
    f.write(textwrap.dedent(s))
    f.seek(0)
