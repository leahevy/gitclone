import os
import os.path
import sys

import pytest
from typer.testing import CliRunner

from gitclone.cli import cli, main

from .utils import coreconfig, write

runner = CliRunner()


def test_cli_clone() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git gitclone
                - https://github.com/leahevy/gitclone.git gitclone2
            """,
        )
        result = runner.invoke(cli, ["clone"])
        assert result.exit_code == 0

        assert os.path.exists(os.path.join("gitclone", ".git"))
        assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_cli_clone_and_pull() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git gitclone
                - https://github.com/leahevy/gitclone.git gitclone2
            """,
        )
        result = runner.invoke(cli, ["clone"])
        assert result.exit_code == 0

        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git gitclone
                - https://github.com/leahevy/gitclone.git gitclone2
            """,
        )
        result = runner.invoke(cli, ["pull"])
        assert result.exit_code != 0  # TODO: Not implemented

        assert os.path.exists(os.path.join("gitclone", ".git"))
        assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_cli_main_clone() -> None:
    with coreconfig() as f:
        write(
            f,
            """
            repositories:
                - https://github.com/leahevy/gitclone.git gitclone
                - https://github.com/leahevy/gitclone.git gitclone2
            """,
        )
        sys.argv = ["gitclone"]
        with pytest.raises(SystemExit) as e:
            main()
        assert e.type == SystemExit
        assert e.value.code == 0

        assert os.path.exists(os.path.join("gitclone", ".git"))
        assert os.path.exists(os.path.join("gitclone2", ".git"))
