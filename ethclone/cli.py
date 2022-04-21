#!/usr/bin/env python3

import sys

from ethclone.gitcmds import clone, GitCloneException, CloneProcess

import yaml
import re
import pathlib

from github import Github


def clone_repos(repos: list[str]):
    repos_existing = []
    repos_to_clone = []
    for repostr in repos:
        result = re.search(r"([^\s]+)\s+as\s+(.+)", repostr)
        if result:
            url = result.group(1)
            dest = result.group(2)

            dest_path = pathlib.Path(dest)

            if not dest_path.exists():
                repos_to_clone.append(CloneProcess(url=url, dest=dest))
            else:
                repos_existing.append(CloneProcess(url=url, dest=dest))
        else:
            raise ValueError(repostr)

    try:
        clone(repos_to_clone)
    except KeyboardInterrupt:
        sys.exit(5)
    except GitCloneException as e:
        print(str(e))
        sys.exit(6)
    finally:
        if repos_existing:
            print(
                f"Info: {len(repos_existing)} of {len(repos_existing) + len(repos_to_clone)} repositories already existed."
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
    clone_repos(repos)
