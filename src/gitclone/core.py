import os
import pathlib
import shutil
from collections import OrderedDict

from github import AuthenticatedUser, Github, NamedUser

from gitclone.config import AuofetchConfig, Config, ConfigManager
from gitclone.exceptions import CoreException
from gitclone.gitcmds import (
    GitAction,
    GitActionMultiprocessingHandler,
    GitCloneAction,
)
from gitclone.repositories import RepoSpecification
from gitclone.utils import print


class GitcloneCore:
    def __init__(
        self,
        config: Config | None = None,
        resolve_config: bool = True,
        load_global: bool = True,
        verbose: bool = False,
    ):
        if not shutil.which("git"):
            raise CoreException("Git is not installed")

        self.configmanager = ConfigManager(verbose=verbose)
        self.verbose = verbose
        if not config:
            if resolve_config:
                config = self.configmanager.get_config(load_global=load_global)
            else:
                config = self.configmanager.get_default_config()
        self.config = config

    def do_clone(
        self,
        repos: list[RepoSpecification],
        dest_root: str = ".",
        verbose: bool = False,
        dry_run: bool = False,
    ) -> None:
        repos = list(OrderedDict.fromkeys(repos))

        repos_existing: list[GitAction] = []
        repos_to_clone: list[GitAction] = []
        for r in repos:
            baseurl, delimiter, path, full_url, branch, dest = r.extract()

            dest = os.path.expanduser(dest)
            dest_root = os.path.expanduser(dest_root)
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
            GitActionMultiprocessingHandler(repos_to_clone).run(
                verbose=verbose, dry_run=dry_run
            )

    def do_resolve_autofetch(
        self, *config: AuofetchConfig
    ) -> list[RepoSpecification]:
        repos: list[RepoSpecification] = []
        for autofetch in config:
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
                        repos.append(
                            RepoSpecification(
                                url=f"git@github.com:{repo.full_name}.git",
                                dest=path,
                            )
                        )
                    elif github.method == "https":
                        repos.append(
                            RepoSpecification(
                                url=f"https://github.com/{repo.full_name}.git",
                                dest=path,
                            )
                        )
                    else:
                        raise CoreException(
                            f"Unknown autofetch github.method: {github.method}"
                        )
                results: list[RepoSpecification] = []
                if github.includes:
                    results.clear()
                    for include in github.includes:
                        innerresults = [r for r in repos if r.matches(include)]
                        results += innerresults
                    repos = results
                if github.excludes:
                    results.clear()
                    for exclude in github.excludes:
                        for r in repos:
                            if not r.matches(exclude):
                                results.append(r)
                    repos = results
        return repos

    def clone(
        self,
        *repos: RepoSpecification,
        verbose: bool | None = None,
        dry_run: bool = False,
        config: Config | None = None,
    ) -> None:
        if not config:
            config = self.config
        if verbose is None:
            verbose = self.verbose
        if dry_run:
            verbose = True
        repos_to_clone = list(repos)
        if not repos_to_clone:
            repos_to_clone = self.do_resolve_autofetch(*config.autofetch)
            if config.repositories:
                repos_to_clone += [
                    RepoSpecification.parse(repostr)
                    for repostr in config.repositories
                ]
        if repos_to_clone:
            self.do_clone(repos_to_clone, config.dest, verbose, dry_run)
            if verbose:
                print("[green]DONE[/]")
        else:
            print(
                "[yellow]No repositories were specified,"
                " nothing to do... exiting[/]"
            )


__all__ = ["GitcloneCore"]
