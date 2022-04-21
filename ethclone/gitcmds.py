import git
from rich import progress
from pathlib import Path
import os
from dataclasses import dataclass
from threading import Thread


class GitRichProgress:
    max_name_length = 20

    def __init__(self):
        super().__init__()

        self.progressbar = progress.Progress(
            progress.SpinnerColumn(),
            progress.TextColumn("{task.description}"),
            progress.BarColumn(),
            progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            progress.TimeRemainingColumn(),
            progress.TextColumn("{task.fields[message]}"),
        )
        self.progressbar = self.progressbar.__enter__()

    def __del__(self) -> None:
        try:
            self.progressbar.__exit__(None, None, None)
        except:
            pass

    def task(self, name: str):
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

        class RemoteProgress(git.RemoteProgress):
            def update(
                self,
                op_code: int,
                cur_count: str | float,
                max_count: float | str | None = None,
                message: str | None = "",
            ) -> None:
                progressbar.update(
                    task_id=task,
                    completed=cur_count,
                    total=max_count,
                    message=message,
                )

            def stop(self):
                progressbar.stop_task(task)
                progressbar.remove_task(task)

        return RemoteProgress()


@dataclass
class CloneProcess:
    url: str
    dest: str
    branch: str | None = None


def _clonefunc(progress, repo, result):
    task = progress.task(repo.dest)
    try:
        dest_path = Path(repo.dest)
        parent_dir = dest_path.parents[0]
        parent_dir.mkdir(parents=True, exist_ok=True)

        if not dest_path.exists():
            git.Repo.clone_from(
                url=repo.url,
                to_path=Path(repo.dest).resolve(),
                progress=task,
                branch=repo.branch,
            )
    except Exception as e:
        task.stop()
        result[repo.dest] = None
        result[repo.dest] = e


class GitCloneException(Exception):
    def __init__(self, exceptions: list[Exception]):
        self.exceptions = exceptions

    def __str__(self):
        return os.linesep.join([str(e) for e in self.exceptions if e is not None])


def clone(repos: list[CloneProcess]) -> None:
    if not repos:
        return
    progress = GitRichProgress()
    threads = []
    result = {}
    for repo in repos:
        threads.append(Thread(target=_clonefunc, args=(progress, repo, result)))
        threads[-1].start()

    for thread in threads:
        thread.join()
    del progress

    for _, e in result.items():
        if e is not None:
            raise GitCloneException(result.values())


if __name__ == "__main__":
    c = CloneProcess(
        url="https://github.com/Homebrew/brew", dest="TEST/1", branch="master"
    )
    c2 = CloneProcess(
        url="https://github.com/Homebrew/brew", dest="TEST/2", branch="master"
    )
    clone([c, c2])
