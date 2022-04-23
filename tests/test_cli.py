from .utils import *


def test_cli_main_repos():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            with open("gitclone.yaml", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                    other:
                        - https://github.com/evyli/gitclone.git gitclone
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
                    https://github.com/evyli/gitclone.git gitclone1
                    https://github.com/evyli/gitclone.git gitclone2
                    """
                    )
                )
            cli.main()
            assert os.path.exists(os.path.join("gitclone1", ".git"))
            assert os.path.exists(os.path.join("gitclone2", ".git"))


def test_cli_main_txt_file_longer_base():
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
            cli.main()
            assert os.path.exists(os.path.join("base", "gitclone", ".git"))


def test_cli_main_txt_file_branch():
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
            cli.main()
            assert os.path.exists(os.path.join("gitclone", ".git"))


def test_cli_main_txt_file_default_dest():
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
            cli.main()
            assert os.path.exists(os.path.join("gitclone", ".git"))


def test_cli_main_noconfig():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with cwd(tmpdirname):
            cli.main()
            assert not len(os.listdir())
