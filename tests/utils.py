import os
import os.path

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
