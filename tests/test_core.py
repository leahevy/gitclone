import os
import os.path

from gitclone.core import GitcloneCore

from .utils import coreconfig, write


def clone() -> None:
    GitcloneCore(load_global=False).clone()


def test_core_main_repos() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git gitclone
                - https://github.com/leahevy/gitclone.git gitclone2
            """,
        )
        clone()
        assert os.path.exists(os.path.join("gitclone", ".git"))
        assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_core_main_autofetch_github() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            autofetch:
                -
                    github:
                        user: leahevy
                        path: "github.com/{user}/{repo}"
                        includes:
                            - .*gitclone.*

            """,
        )
        clone()
        assert os.path.exists(
            os.path.join("github.com", "leahevy", "gitclone", ".git")
        )


def test_core_main_longer_base() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git base/gitclone
            """,
        )
        clone()
        assert os.path.exists(os.path.join("base", "gitclone", ".git"))


def test_core_main_branch() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git@master gitclone
            """,
        )
        clone()
        assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_default_dest() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git
            """,
        )
        clone()
        assert os.path.exists(os.path.join("gitclone", ".git"))


def test_core_main_noconfig() -> None:
    with coreconfig():
        try:
            clone()
            assert False
        except Exception:
            pass
        assert os.listdir() == ["gitclone.yaml"]


def test_core_main_invalid_url() -> None:
    with coreconfig() as f:
        write(
            f,
            "repositories:\n    - "
            "https://some-random-data-1722t2842626182.com/g1231242342353343434"
            " test",
        )
        try:
            clone()
            assert False
        except Exception:
            pass
        assert not os.path.exists("test")
