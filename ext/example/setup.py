#!/usr/bin/env python

import os

from setuptools import find_packages, setup

os.chdir(os.path.dirname(__file__))

with open("requirements.txt", "r") as f:
    required_packages = f.read().strip().split()

with open("requirements-dev.txt", "r") as f:
    required_dev_packages = f.read().strip().split()

with open("README.md", "r") as f:
    long_description = f.read().strip()

setup_info = dict(
    name="pygitclone-example",
    version="0.0.1",
    author="Leah Lackner",
    author_email="leah.lackner+github@gmail.com",
    url="https://github.com/evyli/gitclone/tree/master/ext",
    project_urls={
        "Documentation": "https://github.com/evyli/gitclone/blob/master/"
        "README.md#gitclone",
        "Source": "https://github.com/evyli/gitclone/tree/master/ext",
        "Tracker": "https://github.com/evyli/gitclone/issues",
    },
    description="Example extension package for gitclone",
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
    entry_points={},
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=required_packages,
    extras_require={
        "dev": required_dev_packages,
    },
    cmdclass={},
)
setup(**setup_info)  # type: ignore
