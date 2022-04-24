import os
import os.path

from gitclone.core import clone_from_config as clone

from .utils import *


def test_core_main_repos():
    with coreconfig() as f:
        write(
            f,
            """
        repositories:
            - https://github.com/evyli/gitclone.git gitclone
        """,
        )
        clone()
        assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_autofetch_github():
    with coreconfig() as f:
        write(
            f,
            """
            autofetch:
                -
                    github:
                        user: evyli
                        path: "github.com/{user}/{repo}"
            """,
        )
        clone()
        assert os.path.exists(
            os.path.join("github.com", "evyli", "gitclone", ".git")
        )


def test_core_main_txt_file():
    with textconfig() as f:
        write(
            f,
            """
            https://github.com/evyli/gitclone.git gitclone1
            https://github.com/evyli/gitclone.git gitclone2
            """,
        )
        clone()
        assert os.path.exists(os.path.join("gitclone1", ".git"))
        assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_core_main_txt_file_longer_base():
    with textconfig() as f:
        write(f, "https://github.com/evyli/gitclone.git base/gitclone")
        clone()
        assert os.path.exists(os.path.join("base", "gitclone", ".git"))


def test_core_main_txt_file_branch():
    with textconfig() as f:
        write(f, "https://github.com/evyli/gitclone.git@master gitclone")
        clone()
        assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_txt_file_default_dest():
    with textconfig() as f:
        write(f, "https://github.com/evyli/gitclone.git")
        clone()
        assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_noconfig():
    with textconfig():
        clone()
        assert os.listdir() == ["gitclone.txt"]


def test_core_main_invalid_url():
    with textconfig() as f:
        write(
            f,
            "https://some-random-data-1722t2842626182.com/g1231242342353343434 test",
        )
        try:
            clone()
            assert False
        except Exception:
            pass
        assert not os.path.exists("test")
