import os
import os.path
import tempfile
import textwrap

from contextlib import contextmanager


@contextmanager
def cwd(path):
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
def tempdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            yield


@contextmanager
def coreconfig():
    with tempdir():
        with open("gitclone.yaml", "w+") as f:
            yield f


@contextmanager
def textconfig():
    with tempdir():
        with open("gitclone.txt", "w+") as f:
            yield f


def write(f, s):
    f.write(textwrap.dedent(s))
    f.seek(0)
