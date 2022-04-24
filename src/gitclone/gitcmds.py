import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Thread

from git import RemoteProgress
from git.repo import Repo
from rich import progress

from gitclone.exceptions import GitOperationException


class GitRichProgress:
    max_name_length = 20

    def __init__(self) -> None:
        super().__init__()

        self.progressbar = progress.Progress(
            progress.SpinnerColumn(),
            progress.TextColumn("{task.description}"),
            progress.BarColumn(),
            progress.TextColumn(
                "[progress.percentage]{task.percentage:>3.0f}%"
            ),
            progress.TimeRemainingColumn(),
            progress.TextColumn("{task.fields[message]}"),
        )
        self.progressbar = self.progressbar.__enter__()

    def __del__(self) -> None:
        try:
            self.progressbar.__exit__(None, None, None)
        except Exception:
            pass

    def task(self, name: str):  # type: ignore
        progressbar = self.progressbar

        if len(name) > GitRichProgress.max_name_length - 3:
            name = f"...{name[(-1 * (GitRichProgress.max_name_length-3)):]}"
        name_format = "{0: <%s}" % GitRichProgress.max_name_length
        name = name_format.format(name)

        task = progressbar.add_task(
            description=name,
            total=100.0,
            message="",
        )

        class GitRemoteProgress(RemoteProgress):
            def update(
                self,
                op_code: int,
                cur_count: str | float,
                max_count: float | str | None = None,
                message: str | None = "",
            ) -> None:
                if max_count is None:
                    max_count = 0
                progressbar.update(
                    task_id=task,
                    completed=float(cur_count),
                    total=float(max_count),
                    message=message,
                )

            def stop(self) -> None:
                progressbar.stop_task(task)
                progressbar.remove_task(task)

        return GitRemoteProgress()


@dataclass(frozen=True, eq=True)
class CloneProcess:
    base_url: str
    delimiter: str
    remote_src: str
    full_url: str
    dest: str
    branch: str | None = None


def _clonefunc(
    progress: GitRichProgress,
    repo: CloneProcess,
    result: dict[str, Exception | None],
) -> None:
    task = progress.task(repo.dest)
    try:
        dest_path = Path(repo.dest)
        parent_dir = dest_path.parents[0]
        parent_dir.mkdir(parents=True, exist_ok=True)

        if not dest_path.exists():
            Repo.clone_from(
                url=repo.full_url,
                to_path=Path(repo.dest).resolve(),
                progress=task,
                branch=repo.branch,
                multi_options=["--recurse-submodules"],
            )
        result[repo.dest] = None
    except Exception as e:
        task.stop()
        result[repo.dest] = e


def git_error_to_str(giterror: Exception) -> str:
    if "exit code(128)" in str(giterror):
        return str(giterror) + "\n" + "  Remote repository does not exist."
    return str(giterror)


class ClonePerServerHandler:
    MAX_CONNECTIONS_PER_SERVER = 6
    MAX_CONNECTIONS_TOTAL = sys.maxsize

    def __init__(self, repos: list[CloneProcess]) -> None:
        self.servers: dict[str, list[CloneProcess]] = {}
        self.cur_downloads: dict[str, int] = {}
        self.cur_total_downloads: int = 0

        for repo in repos:
            self.add_download(repo)

    def add_download(self, repo: CloneProcess) -> None:
        if repo.base_url not in self.servers:
            self.servers[repo.base_url] = []
            self.cur_downloads[repo.base_url] = 0
        self.servers[repo.base_url].append(repo)

    def run(self) -> None:
        progress = GitRichProgress()
        threads: dict[CloneProcess, Thread] = {}
        result: dict[str, Exception | None] = {}

        while True:
            for server, repos in list(self.servers.items()):
                for repo in repos[:]:
                    if (
                        self.cur_downloads[server]
                        >= ClonePerServerHandler.MAX_CONNECTIONS_PER_SERVER
                        or self.cur_total_downloads
                        >= ClonePerServerHandler.MAX_CONNECTIONS_TOTAL
                    ):
                        break
                    else:
                        self.cur_downloads[server] += 1
                        self.cur_total_downloads += 1
                        thread = Thread(
                            target=_clonefunc, args=(progress, repo, result)
                        )
                        repos.remove(repo)
                        if not repos:
                            del self.servers[server]
                        threads[repo] = thread
                        thread.start()

            for repo, thread in list(threads.items()):
                if not thread.is_alive():
                    del threads[repo]
                    self.cur_downloads[repo.base_url] -= 1
                    self.cur_total_downloads -= 1
            if not self.servers and not threads:
                break

            time.sleep(1)
        del progress

        for _, e in result.items():
            if e is not None:
                raise GitOperationException(
                    "The following git error occurred:\n"
                    + "\n".join(
                        [
                            git_error_to_str(e)
                            for e in result.values()
                            if e is not None
                        ]
                    )
                )
