<div align="center">
    <img src="https://raw.githubusercontent.com/evyli/gitclone/master/img/gitclone.png" width="350px"</img> 
</div>
<br/>

<p align="center">
<u><b> The git clone utility. </b></u><br><b>Manages multiple git repositories with ease.</b> 
</p>

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/evyli/ethclone/graphs/commit-activity)
[![Build](https://github.com/evyli/gitclone/actions/workflows/build.yml/badge.svg)](https://github.com/evyli/gitclone/actions/workflows/build.yml)
[![Tests](https://github.com/evyli/gitclone/actions/workflows/tests.yml/badge.svg)](https://github.com/evyli/gitclone/actions/workflows/tests.yml)
[![Test coverage](https://raw.githubusercontent.com/evyli/gitclone/master/img/coverage.svg)](https://github.com/evyli/gitclone/tree/master/tests)
[![Coverage met](https://raw.githubusercontent.com/evyli/gitclone/master/img/coverage-met.svg)](https://github.com/evyli/gitclone/tree/master/tests)
[![Typechecks](https://github.com/evyli/gitclone/actions/workflows/typechecks.yml/badge.svg)](https://github.com/evyli/gitclone/actions/workflows/typechecks.yml)
[![Style](https://github.com/evyli/gitclone/actions/workflows/style.yml/badge.svg)](https://github.com/evyli/gitclone/actions/workflows/style.yml)
[![Formatting](https://github.com/evyli/gitclone/actions/workflows/formatchecks.yml/badge.svg)](https://github.com/evyli/gitclone/actions/workflows/formatchecks.yml)
[![Analysis](https://github.com/evyli/gitclone/actions/workflows/analysis.yml/badge.svg)](https://github.com/evyli/gitclone/actions/workflows/analysis.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

# 💡 Gitclone 

**Gitclone** allows you to *manage* multiple **git** repositories in a *directory structure*.

<br/>
<div align="center">
    <img src="https://raw.githubusercontent.com/evyli/gitclone/master/img/terminalizer/demo.gif" width="600px"</img> 
</div>
<br/>

Currently this is **still in heavy development**. This Readme will be updated when it is ready. Use at your own risk at this moment.

---

### Table of Contents

* [Installation](#-installation)
* [Features](#-features)
* [Configuration](#%EF%B8%8F-configuration)
* [Usage](#-usage)
* [Planned Features](#-planned-features)
* [Contributing](#-contributing)
* [Extensions](#-extensions)
* [License](#-license)

---

### 💻 Installation 

Install the python package with `pip install -e .`. It will be published on **pip** as soon as it is ready.

---

### 💫 Features

- Clone specified *git repositories* in local directory.
- Use a local *configuration* file.
- Autofetch with **github.com** to automatically clone all your owned repositories, including *private* ones if you specify an API token.
- **Typechecked** library code.

---

### ⌨️ Configuration

Change values in directory local file `gitclone.yaml` to your needs. You can copy the file from `gitclone.example.yaml`. A config generation is under development.

---

### 😎 Usage

Run `gitclone` from the same directory. Your configured git repositories will be cloned.

---

### 🔮 Planned Features

- **Pull** in existing directories.
- **Find** local git directories.
- **Config generation**.
- Using of **credential stores** for used API tokens.
- Better **CLI**.

---

### 👭 Contributing

👋 Want to add a contribution to **gitclone**? Feel free to send me a [pull request](https://github.com/evyli/gitclone/compare).

See also [here](https://github.com/evyli/gitclone/blob/master/CONTRIBUTING.md).

---

### 📡 Extensions

To learn how to include an extension in **Gitclone** see [here](https://github.com/evyli/gitclone/blob/master/src/gitclone/extensions/README.md).

---

### 📝 License

Copyright (C)  2022 Leah Lackner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
