#!/usr/bin/env python
from setuptools import find_packages, setup

import distutils.cmd
import subprocess
import os
import sys
import shutil

from threading import Thread
from queue import Queue

os.chdir(os.path.dirname(__file__))

REQUIRED_COVERAGE = 80


class BaseCommand(distutils.cmd.Command):
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


class ReleaseCommand(BaseCommand):
    description = "Prepare release"

    def run(self):
        shell("python setup.py format")
        shell("python setup.py style")
        shell("python setup.py typechecks")
        shell("python setup.py test")
        shell("python setup.py badges")


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

with open("VERSION", "r") as f:
    version = f.read().strip()
shutil.copyfile("VERSION", "src/gitclone/VERSION")

setup_info = dict(
    name="gitclone",
    version=version,
    author="Leah Lackner",
    author_email="leah.lackner+github@gmail.com",
    url="https://github.com/evyli/gitclone",
    project_urls={
        "Documentation": "https://github.com/evyli/gitclone/blob/master/README.md#ethclone",
        "Source": "https://github.com/evyli/gitclone",
        "Tracker": "https://github.com/evyli/gitclone/issues",
    },
    description="Gitclone allows you to manage multiple git repositories in a directory structure with ease ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms="Linux, Mac OSX",
    license="GPLv3",
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPLv3",
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
    cmdclass={
        "typechecks": shellcommand(
            "Typechecks", "mypy --pretty --strict src tests", "Run typechecks"
        ),
        "style": shellcommand(
            "Stylechecks",
            [
                "flake8 --select=E9,F63,F7,F82 --show-source --statistics src tests",
                "flake8 --max-complexity=10 --max-line-length=127 --statistics src tests",
            ],
            "Run stylechecks",
        ),
        "format": shellcommand("Format", "black -l 80 src tests", "Run formatter"),
        "check_format": shellcommand(
            "FormatCheck", "black --check -l 80 src tests", "Run formatter"
        ),
        "test": shellcommand(
            "Test", "pytest --cov-report html --cov=gitclone tests", "Run tests"
        ),
        "badges": BadgesCommand,
        "release": ReleaseCommand,
    },
)
setup(**setup_info)
