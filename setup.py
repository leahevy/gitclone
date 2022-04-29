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
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


def reader(pipe, queue):
    try:
        with pipe:
            for line in iter(pipe.readline, b""):
                queue.put((pipe, line))
    finally:
        queue.put(None)


def shell(cmd):
    print(cmd)
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    q = Queue()
    Thread(target=reader, args=[p.stdout, q]).start()
    Thread(target=reader, args=[p.stderr, q]).start()
    for _ in range(2):
        for source, line in iter(q.get, None):
            print(line.decode("utf-8"))
    p.communicate()
    if p.returncode != 0:
        sys.exit(p.returncode)


def shellcommand(name, cmd, desc=None):
    class InnerClass(BaseCommand):
        description = desc
        if description is None:
            description = cmd

        def run(self):
            if isinstance(cmd, list):
                for c in cmd:
                    shell(c)
            else:
                shell(cmd)

    InnerClass.__name__ = name + "Command"
    return InnerClass


class PreCommitCommand(BaseCommand):
    description = "Prepare a commit"

    def run(self):
        shell("./setup.py check_format >/dev/null || ./setup.py check_format")
        shell("./setup.py style >/dev/null || ./setup.py style")
        shell("./setup.py typechecks >/dev/null || ./setup.py typechecks")


class CheckFormatCommand(BaseCommand):
    description = "Test formatting"

    def run(self):
        shell("isort --check -l 79 src tests ext")
        shell("black --check -l 79 src tests ext")


class FormatCommand(BaseCommand):
    description = "Run formatter"

    def run(self):
        shell("isort -l 79 .")
        shell("black -l 79 .")


class BadgesCommand(BaseCommand):
    description = "Generate badges"

    def run(self):
        import anybadge
        from coverage import coverage

        cov = coverage()
        cov.load()
        total = int(cov.report())

        thresholds = {20: "red", 40: "orange", 60: "yellow", 100: "green"}
        badge = anybadge.Badge(
            "Test coverage", total, value_suffix="%", thresholds=thresholds
        )
        try:
            os.remove(os.path.join("img", "coverage.svg"))
        except Exception:
            pass
        badge.write_badge(os.path.join("img", "coverage.svg"))

        thresholds = {"passing": "green", "failing": "red"}
        badge = anybadge.Badge(
            f"Coverage>={REQUIRED_COVERAGE}%",
            "passing" if total >= REQUIRED_COVERAGE else "failing",
            thresholds=thresholds,
        )
        try:
            os.remove(os.path.join("img", "coverage-met.svg"))
        except Exception:
            pass
        badge.write_badge(os.path.join("img", "coverage-met.svg"))


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
    url="https://github.com/evyli/gitclone",
    project_urls={
        "Documentation": "https://github.com/evyli/gitclone/blob/master/README.md#gitclone",
        "Source": "https://github.com/evyli/gitclone",
        "Tracker": "https://github.com/evyli/gitclone/issues",
    },
    description="Gitclone allows you to manage multiple git repositories in a directory structure with ease",
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
            "Run typechecks",
        ),
        "style": shellcommand(
            "Stylechecks",
            [
                "flake8 --select=E9,F63,F7,F82 --show-source src tests ext",
                "flake8 --max-complexity=13 --show-source --max-line-length=79 src tests ext",
            ],
            "Run stylechecks",
        ),
        "format": FormatCommand,
        "check_format": CheckFormatCommand,
        "test": shellcommand(
            "Test",
            "pytest src ext tests",
            "Run tests",
        ),
        "badges": BadgesCommand,
        "pre_commit": PreCommitCommand,
    },
)
setup(**setup_info)  # type: ignore
