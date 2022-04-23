import tempfile
import textwrap

from gitclone.core import clone_from_config as clone

from .utils import *


def test_core_main_repos():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.yaml", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    repositories:
                        - https://github.com/evyli/gitclone.git gitclone
                    """
                    )
                )
            clone()
            assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_autofetch_github():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.yaml", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    autofetch:
                        -
                            github:
                                user: evyli
                                path: "github.com/{user}/{repo}"
                    """
                    )
                )
            clone()
            assert os.path.exists(
                os.path.join("github.com", "evyli", "gitclone", ".git")
            )


def test_core_main_txt_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.txt", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    https://github.com/evyli/gitclone.git gitclone1
                    https://github.com/evyli/gitclone.git gitclone2
                    """
                    )
                )
            clone()
            assert os.path.exists(os.path.join("gitclone1", ".git"))
            assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_core_main_txt_file_longer_base():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.txt", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    https://github.com/evyli/gitclone.git base/gitclone
                    """
                    )
                )
            clone()
            assert os.path.exists(os.path.join("base", "gitclone", ".git"))


def test_core_main_txt_file_branch():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.txt", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    https://github.com/evyli/gitclone.git@master gitclone
                    """
                    )
                )
            clone()
            assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_txt_file_default_dest():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.txt", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    https://github.com/evyli/gitclone.git
                    """
                    )
                )
            clone()
            assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_noconfig():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            clone()
            assert not len(os.listdir())
