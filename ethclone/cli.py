#!/usr/bin/env python3
from rich import print

import sys
import os

from ethclone.gitcmds import clone, GitCloneException, CloneProcess

import yaml
import re
import pathlib

from github import Github


def clone_repos(repos: list[str]):
    repos_existing = []
    repos_to_clone = []
    for repostr in repos:
        result = re.search(r"([^\s]+)\s+at\s+([^\s]+)\s+as\s+(.+)", repostr)
        if result:
            base_url = result.group(1)
            remote_src = result.group(2)
            dest = result.group(3)

            dest_path = pathlib.Path(dest)

            process = CloneProcess(base_url=base_url, remote_src=remote_src, dest=dest)
            if not dest_path.exists():
                repos_to_clone.append(process)
            else:
                repos_existing.append(process)
        else:
            print(
                f"[red]Error:[/]{os.linesep}"
                f"  [red]Got[/] [yellow]'{repostr}[/]{os.linesep}"
                "  [red]Expected[/] [green]BASEURL[/] [blue]at[/]"
                " [green]REMOTE_SRC[/] [blue]as[/] [green]LOCAL_DEST_DIR[/]"
            )
            sys.exit(7)

    try:
        clone(repos_to_clone)
    except KeyboardInterrupt:
        sys.exit(5)
    except Exception as e:
        print(f"[red]{str(e)}[/]")
        sys.exit(6)
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
            else:
                g = Github()
                user = g.get_user(v["user"])
            for repo in user.get_repos(
                visibility="all" if v["private-repos"] else "public"
            ):
                path = v["path"]
                path = path.replace("{user}", user.login)
                path = path.replace("{repo}", repo.name)
                if v["method"] == "ssh":
                    repos.append(f"git@github.com: at {repo.full_name}.git as {path}")
                elif v["method"] == "https":
                    repos.append(
                        f"https://github.com at {repo.full_name}.git as {path}"
                    )
                else:
                    raise ValueError(v["method"])
        else:
            print(f"Unsupported autofetch: {k}", file=sys.stderr)
            sys.exit(2)
    return repos


def main():
    print("[green]Reading configuration file: [blue]ethclone.yaml[/][/]")
    with open("ethclone.yaml", "r") as f:
        try:
            y = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

    repos = []
    if "autofetch" in y:
        repos += handle_autofetch(y["autofetch"])
    if "other" in y:
        repos += y["other"]
    clone_repos(repos)
    print("[green]DONE[/]")
