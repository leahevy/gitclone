import sys
import os
import shutil
import pathlib

from collections import OrderedDict

import yaml

from github import Github

from gitclone.config import Config
from gitclone.utils import print
from gitclone.urls import parse_url
from gitclone.gitcmds import ClonePerServerHandler, CloneProcess
from gitclone.exceptions import (
    CoreException,
    ConfigException,
)


def clone_repos(repos: list[str]):
    repos = list(OrderedDict.fromkeys(repos))

    repos_existing = []
    repos_to_clone = []
    for repostr in repos:
        baseurl, path, branch, dest = parse_url(repostr)
        dest_path = pathlib.Path(dest)

        process = CloneProcess(
            base_url=baseurl, remote_src=path, dest=dest, branch=branch or None
        )
        if not dest_path.exists():
            repos_to_clone.append(process)
        else:
            repos_existing.append(process)
    try:
        ClonePerServerHandler(repos_to_clone).run()
    finally:
        if repos_existing:
            print(
                f"[yellow]Info:[/] {len(repos_existing)} of {len(repos_existing) + len(repos_to_clone)} repositories already existed."
            )


def handle_autofetch(y):
    repos = []
    for k, v in y.items():
        if k == "github.com":
            if "token" in v:
                g = Github(v["token"])
                user = g.get_user()
                remote_repos = user.get_repos(
                    visibility="all" if v["private-repos"] else "public"
                )
            else:
                g = Github()
                user = g.get_user(v["user"])
                remote_repos = user.get_repos()
            for repo in remote_repos:
                path = v["path"]
                path = path.replace("{user}", user.login)
                path = path.replace("{repo}", repo.name)
                if v["method"] == "ssh":
                    repos.append(f"git@github.com:{repo.full_name}.git {path}")
                elif v["method"] == "https":
                    repos.append(f"https://github.com/{repo.full_name}.git {path}")
                else:
                    raise ConfigException(
                        f"Unknown autofetch method for github.com: {v['method']}",
                        file="Unknown",
                        key="autofetch.github.com.method",
                        value=v["method"],
                        expected=["ssh", "https"],
                    )
        else:
            print(f"Unsupported autofetch: {k}", file=sys.stderr)
            sys.exit(2)
    return repos


def clone():
    if not shutil.which("git"):
        raise CoreException("Git is not installed")

    repos = []
    if os.path.exists("gitclone.yaml"):
        print("[green]Reading configuration file: [blue]gitclone.yaml[/][/]")
        with open("gitclone.yaml", "r") as f:
            config_str = os.linesep.join(["--- !yamlable/gitclone.Config", f.read()])
            config = yaml.safe_load(config_str)

            repos += handle_autofetch(config.autofetch)
            repos += config.other or []
    if os.path.exists("gitclone.txt"):
        print(
            "[green]Reading additional repositories from file: [blue]gitclone.txt[/][/]"
        )
        with open("gitclone.txt", "r") as f:
            repos += [
                line.strip()
                for line in f.read().strip().split(os.linesep)
                if line.strip()
            ]
    if repos:
        clone_repos(repos)
        print("[green]DONE[/]")
    else:
        print("[orange]No repositories were specified, nothing to do... exiting[/]")
