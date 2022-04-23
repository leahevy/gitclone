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


def handle_autofetch(config):
    repos = []
    for autofetch in config.autofetch:
        if autofetch.github:
            github = autofetch.github
            if github.token:
                g = Github(github.token)
                user = g.get_user()
                remote_repos = user.get_repos(
                    visibility="all" if github.private else "public"
                )
            else:
                g = Github()
                user = g.get_user(github.user)
                remote_repos = user.get_repos()
            for repo in remote_repos:
                path = github.path
                path = path.replace("{user}", user.login)
                path = path.replace("{repo}", repo.name)
                if github.method == "ssh":
                    repos.append(f"git@github.com:{repo.full_name}.git {path}")
                elif github.method == "https":
                    repos.append(f"https://github.com/{repo.full_name}.git {path}")
                else:
                    assert False
    return repos


def clone():
    if not shutil.which("git"):
        raise CoreException("Git is not installed")

    repos = []
    if os.path.exists("gitclone.yaml"):
        print("[green]Reading configuration file: [blue]gitclone.yaml[/][/]")
        config = Config.from_path("gitclone.yaml")
        repos += handle_autofetch(config)
        repos += config.other
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
