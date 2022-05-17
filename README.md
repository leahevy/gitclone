<div align="center">
<img src="https://raw.githubusercontent.com/evyli/gitclone/master/img/gitclone.png" width="350px"></img> 
</div>
<br/>

<p align="center">
<b> The git clone utility. </b><br><b>Manages multiple git repositories with ease.</b> 
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

# Gitclone / Pygitclone

**Gitclone** allows you to *manage* multiple **git** repositories in a *directory structure*.

<br/>
<div align="center">
    <img src="https://raw.githubusercontent.com/evyli/gitclone/master/img/terminalizer/demo.gif" width="600px"></img> 
</div>
<br/>

Currently this is **still in heavy development**. This Readme will be updated when it is ready. Use at your own risk at this moment.

<br/><br/>

---

## Table of Contents

* [Installation](#installation)
* [Features](#features)
* [Configuration](#configuration)
* [Usage](#usage)
* [Contributing](#contributing)
* [Extensions](#extensions)
* [License](#license)

<br/><br/>

---

## Installation 

First install the prerequisites required by **GitClone**:

<details>
    <summary>Linux</summary>

On Linux install **git** with your package manager, e.g.:

```bash
apt install git
```
</details>

<details>
    <summary>MacOS</summary>

On MacOS install **git** with the *Xcode Command Line Tools*, e.g.:

```bash
xcode-select --install
```
</details>

<details>
    <summary>Windows</summary>

Although not tested on Windows, you can install **git** by visiting [the git website](https://git-scm.com/download/win]).
</details>

<br/>

Install the Python package with `pip install pygitclone`.

To install the shell completion run:
```bash
gitclone --install-completion [bash|zsh|fish|powershell|pwsh]
```

<br/><br/>

---

## Features

- Clone specified *git repositories* in local directory.
- Use a local *configuration* file.
- Autofetch with **github.com** to automatically clone all your owned repositories, including *private* ones if you specify an API token.
- **Typechecked** library code.

<br/><br/>

---

## Configuration

You can use the configuration generator to get started by running:

```bash
gitclone config --help
```

An example (`gitclone.yml` or `.gitclone.yml`) configuration file might look like this:

```yaml
dest: ./

autofetch:
  -
    github:
      user: GITHUB_USER
      method: ssh
      token: GITHUB_TOKEN
      private: true
      path: "github.com/{user}/{repo}"


repositories:
  - https://example.com/some/repository/url.git some/destination
```

The configuration file can either be global (in `~/.config/gitclone.yml`) or local (`./gitclone.yml`).

<br/><br/>

---

## Usage

Run `gitclone` from the same directory. Your configured git repositories will be cloned.

The supported commands are:
- **clone**: Clones the configured git repositories (The default command if no command is specified).
- **pull**: Pull new changes in the cloned repositories.

To get more informaion run `gitclone --help`.

<br/><br/>

---

## Contributing

Want to add a contribution to **gitclone**? Feel free to send me a [pull request](https://github.com/evyli/gitclone/compare).

See also [here](https://github.com/evyli/gitclone/blob/master/CONTRIBUTING.md).

<br/><br/>

---

## Extensions

To learn how to include an extension in **Gitclone** see [here](https://github.com/evyli/gitclone/blob/master/src/gitclone/extensions/README.md).

<br/><br/>

---

## License

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
