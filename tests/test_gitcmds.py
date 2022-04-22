import gitclone.gitcmds as gitcmds
import gitclone.cli as cli

import tempfile
import os
import os.path
import sys
from contextlib import contextmanager
import textwrap


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    assert os.getcwd() != ("/")
    try:
        yield
    finally:
        os.chdir(oldpwd)


def test_cli_main():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.yaml", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    other:
                        - https://github.com at evyli/gitclone.git as gitclone
                    """
                    )
                )
            cli.main()
            assert os.path.exists(os.path.join("gitclone", ".git"))
