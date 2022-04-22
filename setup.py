#!/usr/bin/env python
from setuptools import find_packages, setup

import pathlib
import distutils.cmd
import subprocess


class TestCommand(distutils.cmd.Command):
    description = "Run pytest with coverage"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = [
            "pytest",
            "--cov-report",
            "html",
            f"--cov=gitclone",
            str(pathlib.Path("tests").resolve()),
        ]
        subprocess.check_call(command)


with open("requirements.txt", "r") as f:
    required_packages = f.read().strip().split()

setup_info = dict(
    name="gitclone",
    version="0.0.2",
    author="Leah Lackner",
    author_email="leah.lackner+github@gmail.com",
    url="https://github.com/evyli/gitclone",
    project_urls={
        "Documentation": "https://github.com/evyli/gitclone/blob/master/README.md#ethclone",
        "Source": "https://github.com/evyli/gitclone",
        "Tracker": "https://github.com/evyli/gitclone/issues",
    },
    description="Project to pull git repositories into directory structure",
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
    package_dir={"": "."},
    packages=find_packages(where="."),
    install_requires=required_packages,
    cmdclass={
        "test": TestCommand,
    },
)
setup(**setup_info)
