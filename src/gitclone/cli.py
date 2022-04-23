import sys
import os
import shutil
import re
import pathlib
import urllib

from collections import OrderedDict

import yaml

from rich import print
from yamlable import YamlAble, yaml_info
from github import Github

from gitclone.gitcmds import ClonePerServerHandler, CloneProcess


def rpartition(s, d):
    res = s.rpartition(d)
    if res[0]:
        return (res[0], res[2])
    return (res[2], res[0])


def split_url_branch(given_url):
    url, branch = rpartition(given_url, "@")
    url = url.strip()
    branch = branch.strip()
    if "/" in branch:
        url = given_url
        branch = ""
    return url, branch


def parse_url(repostr):
    repostr.strip()
    url, dest = rpartition(repostr, " ")
    url = url.strip()
    dest = dest.strip()

    ssh_url_re = r"([^@ ]+@[^:]+:)(.*)"
    result = re.search(ssh_url_re, url)
    if result:
        baseurl = result.group(1)
        path = result.group(2)

        if "@" in path:
            url, branch = split_url_branch(url)
        else:
            url, branch = url, ""
    else:
        url, branch = split_url_branch(url)

        url = urllib.parse.urlparse(url)
        resstr = []
        if url.scheme:
            resstr.append(url.scheme)
            resstr.append("://")
        resstr.append(url.netloc)

        baseurl = "".join(resstr)

        if url.path:
            path = url.path[1:]
        else:
            path = url.path

    if not dest:
        dest = path.split("/")[-1]
    if dest.endswith(".git"):
        dest = dest[: len(dest) - len(".git")]

    if not baseurl or not path:
        raise ValueError(
            f"[red]Error:[/]{os.linesep}"
            f"  [red]Got invalid repository url[/] [yellow]'{repostr}'[/]{os.linesep}"
            "  [red]Expected[/] [green]url[/][blue]@[/][green]branch[/] or just [green]url[/]"
        )

    return (baseurl, path, branch, dest)


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
                    raise ValueError(v["method"])
        else:
            print(f"Unsupported autofetch: {k}", file=sys.stderr)
            sys.exit(2)
    return repos


@yaml_info(yaml_tag_ns="gitclone")
class Config(YamlAble):
    def __init__(self, autofetch={}, other=None, dest="."):
        self.autofetch = autofetch
        self.other = other


def main():
    try:
        if not shutil.which("git"):
            raise ValueError("Git is not installed")

        repos = []
        if os.path.exists("gitclone.yaml"):
            print("[green]Reading configuration file: [blue]gitclone.yaml[/][/]")
            with open("gitclone.yaml", "r") as f:
                config_str = os.linesep.join(
                    ["--- !yamlable/gitclone.Config", f.read()]
                )
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
    except KeyboardInterrupt:
        print(f"[red]Aborted by user...[/]")
        sys.exit(5)
    except Exception as e:
        print(f"[red]{str(e)}[/]")
        sys.exit(6)
