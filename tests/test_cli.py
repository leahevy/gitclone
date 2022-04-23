import gitclone.gitcmds as gitcmds
import gitclone.cli as cli

import tempfile
import os
import os.path
import sys
import textwrap

from contextlib import contextmanager


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    assert os.getcwd() != ("/")
    try:
        yield
    finally:
        os.chdir(oldpwd)


def test_cli_main_repos():
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


def test_cli_main_autofetch_github():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.yaml", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    autofetch:
                        github.com:
                            user: evyli
                            method: https
                            private-repos: false
                            path: "github.com/{user}/{repo}"
                    """
                    )
                )
            cli.main()
            assert os.path.exists(
                os.path.join("github.com", "evyli", "gitclone", ".git")
            )


def test_cli_main_txt_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.txt", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    https://github.com at evyli/gitclone.git as gitclone1
                    https://github.com at evyli/gitclone.git as gitclone2
                    """
                    )
                )
            cli.main()
            assert os.path.exists(os.path.join("gitclone1", ".git"))
            assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_cli_main_noconfig():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            cli.main()
            assert not len(os.listdir())
