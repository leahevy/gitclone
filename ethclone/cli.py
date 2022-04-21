#!/usr/bin/env python3

import sys

from ethclone.gitcmds import clone, GitCloneException, CloneProcess

import yaml
import re
import pathlib

from github import Github


def clone_repo(repostr: str):
    result = re.search(r"([^\s]+)\s+as\s+(.+)", repostr)
    if result:
        url = result.group(1)
        dest = result.group(2)
        dest_path = pathlib.Path(dest)
        parent_dir = dest_path.parents[0]
        parent_dir.mkdir(parents=True, exist_ok=True)

        if not dest_path.exists():
            try:
                print(f"Cloning {url} to {dest}")
                clone([CloneProcess(url=url, dest=dest)])
                print()
            except KeyboardInterrupt:
                sys.exit(5)
            except GitCloneException as e:
                print(str(e))
                sys.exit(6)
        else:
            print(f"Repository {dest} exists")

    else:
        raise ValueError(repostr)


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
                    repos.append(f"git@github.com:{repo.full_name}.git as {path}")
                elif v["method"] == "https":
                    repos.append(f"https://github.com/{repo.full_name}.git as {path}")
                else:
                    raise ValueError(v["method"])
        else:
            print(f"Unsupported autofetch: {k}", file=sys.stderr)
            sys.exit(2)
    return repos


def main():
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
    for repo in repos:
        clone_repo(repo)
