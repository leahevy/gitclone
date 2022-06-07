#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
from queue import Queue
from threading import Thread

from setuptools import Command, find_packages, setup

os.chdir(os.path.dirname(__file__))

REQUIRED_COVERAGE = 80


class BaseCommand(Command):
    user_options: list[str] = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass


def reader(pipe, queue: Queue):  # type: ignore
    try:
        with pipe:
            for line in iter(pipe.readline, b""):  # type: ignore
                queue.put((pipe, line))  # type: ignore
    finally:
        queue.put(None)  # type: ignore


def shell(cmd: str) -> None:
    print(cmd)
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    q = Queue()  # type: ignore
    Thread(target=reader, args=[p.stdout, q]).start()  # type: ignore
    Thread(target=reader, args=[p.stderr, q]).start()  # type: ignore
    for _ in range(2):
        for source, line in iter(q.get, None):  # type: ignore
            print(line.decode("utf-8"))  # type: ignore
    p.communicate()
    if p.returncode != 0:
        sys.exit(p.returncode)


def shellcommand(
    name: str, cmd: list[str] | str, desc: str | None = None
) -> type[BaseCommand]:
    class InnerClass(BaseCommand):
        description = desc
        if description is None:
            description = str(cmd)

        def run(self) -> None:
            if isinstance(cmd, list):
                for c in cmd:
                    shell(c)
            else:
                shell(cmd)

    InnerClass.__name__ = name + "Command"
    return InnerClass


class PreCommitCommand(BaseCommand):
    description = "Prepare a commit"

    def run(self) -> None:
        shell("./setup.py check_format >/dev/null || ./setup.py check_format")
        shell("./setup.py style >/dev/null || ./setup.py style")
        shell("./setup.py typechecks >/dev/null || ./setup.py typechecks")


class CheckFormatCommand(BaseCommand):
    description = "Test formatting"

    def run(self) -> None:
        shell("isort --check -l 79 .")
        shell("black --check -l 79 .")


class FormatCommand(BaseCommand):
    description = "Run formatter"

    def run(self) -> None:
        shell("isort -l 79 .")
        shell("black -l 79 .")


class BadgesCommand(BaseCommand):
    description = "Generate badges"

    def run(self) -> None:
        import anybadge  # type: ignore
        from coverage import coverage  # type: ignore

        cov = coverage()
        cov.load()  # type: ignore
        total = int(cov.report())  # type: ignore

        thresholds = {20: "red", 40: "orange", 60: "yellow", 100: "green"}
        badge = anybadge.Badge(  # type: ignore
            "Test coverage", total, value_suffix="%", thresholds=thresholds
        )
        try:
            os.remove(os.path.join("img", "coverage.svg"))
        except Exception:
            pass
        badge.write_badge(os.path.join("img", "coverage.svg"))  # type: ignore

        thresholds_str = {"passing": "green", "failing": "red"}
        badge = anybadge.Badge(  # type: ignore
            f"Coverage>={REQUIRED_COVERAGE}%",
            "passing" if total >= REQUIRED_COVERAGE else "failing",
            thresholds=thresholds_str,
        )
        try:
            os.remove(os.path.join("img", "coverage-met.svg"))
        except Exception:
            pass
        badge.write_badge(  # type: ignore
            os.path.join("img", "coverage-met.svg")
        )


with open("requirements.txt", "r") as f:
    required_packages = f.read().strip().split()

with open("requirements-dev.txt", "r") as f:
    required_dev_packages = f.read().strip().split()

with open("VERSION", "r") as f:
    version = f.read().strip()
shutil.copyfile("VERSION", "src/gitclone/VERSION")

with open("README.md", "r") as f:
    long_description = f.read().strip()

setup_info = dict(
    name="pygitclone",
    version=version,
    author="Leah Lackner",
    author_email="leah.lackner+github@gmail.com",
    url="https://github.com/leahevy/gitclone",
    project_urls={
        "Documentation": "https://github.com/leahevy/gitclone"
        "/blob/master/README.md#gitclone",
        "Source": "https://github.com/leahevy/gitclone",
        "Tracker": "https://github.com/leahevy/gitclone/issues",
    },
    description="Gitclone allows you to manage multiple "
    "git repositories in a directory structure with ease",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms="Linux, Mac OSX",
    license="GPLv3",
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General"
        " Public License v3 or later (GPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=True,
    entry_points={
        "console_scripts": ["gitclone=gitclone.cli:main"],
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=required_packages,
    extras_require={
        "dev": required_dev_packages,
    },
    cmdclass={
        "typechecks": shellcommand(
            "Typechecks",
            [
                "mypy --pretty "
                "--warn-unused-configs "
                "--disallow-any-generics "
                "--disallow-subclassing-any "
                "--disallow-untyped-calls "
                "--disallow-untyped-defs "
                "--disallow-incomplete-defs "
                "--check-untyped-defs "
                "--disallow-untyped-decorators "
                "--no-implicit-optional "
                "--warn-redundant-casts "
                "--warn-return-any "
                "--no-implicit-reexport "
                "--strict-equality "
                "src tests ext",
                "mypy --pretty "
                "--warn-unused-configs "
                "--disallow-any-generics "
                "--disallow-subclassing-any "
                "--disallow-untyped-calls "
                "--disallow-untyped-defs "
                "--disallow-incomplete-defs "
                "--check-untyped-defs "
                "--disallow-untyped-decorators "
                "--no-implicit-optional "
                "--warn-redundant-casts "
                "--warn-return-any "
                "--no-implicit-reexport "
                "--strict-equality "
                "setup.py",
            ],
            "Run typechecks",
        ),
        "style": shellcommand(
            "Stylechecks",
            [
                "flake8 --select=E9,F63,F7,F82 --show-source .",
                "flake8 --max-complexity=13 --show-source"
                " --max-line-length=79 .",
            ],
            "Run stylechecks",
        ),
        "format": FormatCommand,
        "check_format": CheckFormatCommand,
        "test": shellcommand(
            "Test",
            "pytest .",
            "Run tests",
        ),
        "badges": BadgesCommand,
        "pre_commit": PreCommitCommand,
    },
)
setup(**setup_info)  # type: ignore
