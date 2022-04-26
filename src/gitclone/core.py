import os
import pathlib
import re
import shutil
from collections import OrderedDict

from github import AuthenticatedUser, Github, NamedUser

from gitclone.config import Config, GlobalConfig, TextConfig
from gitclone.exceptions import CoreException
from gitclone.gitcmds import ClonePerServerHandler, GitAction, GitCloneAction
from gitclone.urls import parse_url
from gitclone.utils import print


def clone_repos(
    config: Config,
    repos: list[str],
    verbose: bool = False,
    dry_run: bool = False,
) -> None:
    repos = list(OrderedDict.fromkeys(repos))

    repos_existing: list[GitAction] = []
    repos_to_clone: list[GitAction] = []
    for repostr in repos:
        baseurl, delimiter, path, full_url, branch, dest = parse_url(repostr)

        dest = os.path.expanduser(dest)
        dest_root = os.path.expanduser(config.dest)
        if not os.path.isabs(dest):
            dest = os.path.join(dest_root, dest)

        dest_path = pathlib.Path(dest)

        action = GitCloneAction(
            base_url=baseurl,
            remote_src=path,
            delimiter=delimiter,
            full_url=full_url,
            dest=dest,
            branch=branch or None,
        )
        if not dest_path.exists():
            repos_to_clone.append(action)
        else:
            repos_existing.append(action)
    if repos_existing and repos_to_clone:
        print(
            f"[yellow]Info:[/] {len(repos_existing)} of"
            f" {len(repos_existing) + len(repos_to_clone)}"
            " repositories already exist."
        )
    if repos_existing and not repos_to_clone:
        print("[yellow]Info:[/] All repositoried already exist")
    if repos_to_clone:
        ClonePerServerHandler(repos_to_clone).run(
            verbose=verbose, dry_run=dry_run
        )


def handle_autofetch(config: Config) -> list[str]:
    repos: list[str] = []
    for autofetch in config.autofetch:
        if autofetch.github:
            github = autofetch.github

            user: (
                NamedUser.NamedUser | AuthenticatedUser.AuthenticatedUser
            ) | None = None
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
                    repos.append(
                        f"https://github.com/{repo.full_name}.git {path}"
                    )
                else:
                    assert False
            results: list[str] = []
            if github.includes:
                results.clear()
                for include in github.includes:
                    innerresults = [r for r in repos if re.match(include, r)]
                    results += innerresults
                repos = results
            if github.excludes:
                results.clear()
                for exclude in github.excludes:
                    for repo_str in repos:
                        if not re.match(exclude, repo_str):
                            results.append(repo_str)
                repos = results
    return repos


def clone_single(
    repo_tuple: tuple[str, str],
    verbose: bool = False,
    debug: bool = False,
    dry_run: bool = False,
) -> None:
    repostr = repo_tuple[0]
    if repo_tuple[1] is not None:
        repostr = " ".join([repostr, repo_tuple[1]])
    clone_from_config([repostr], verbose=verbose, debug=debug, dry_run=dry_run)


def clone_from_config(
    repos: list[str] | None = None,
    verbose: bool = False,
    debug: bool = False,
    dry_run: bool = False,
) -> None:
    if not shutil.which("git"):
        raise CoreException("Git is not installed")

    globalconfig = GlobalConfig()
    if not repos:
        repos = []
        if os.path.exists("gitclone.yaml"):
            if verbose:
                print(
                    "[green]Reading configuration file:"
                    " [blue]gitclone.yaml[/][/]"
                )
            globalconfig.config = Config.from_path("gitclone.yaml")
            repos += handle_autofetch(globalconfig.config)
            if globalconfig.config.repositories:
                repos += globalconfig.config.repositories
        if os.path.exists("gitclone.txt"):
            print(
                "[green]Reading additional repositories from file:"
                " [blue]gitclone.txt[/][/]"
            )
            globalconfig.textconfig = TextConfig.from_path("gitclone.txt")
            if globalconfig.textconfig.repositories:
                repos += globalconfig.textconfig.repositories
    if repos:
        clone_repos(globalconfig.config, repos, verbose, dry_run)
        if verbose:
            print("[green]DONE[/]")
    else:
        print(
            "[orange]No repositories were specified,"
            " nothing to do... exiting[/]"
        )
