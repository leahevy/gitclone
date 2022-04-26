import time
from dataclasses import dataclass
from multiprocessing.pool import ThreadPool
from pathlib import Path
from threading import RLock
from typing import Protocol

from git import RemoteProgress
from git.repo import Repo
from rich import progress
from rich.console import Console

from gitclone.exceptions import GitOperationException


class GitRemoteProgress(RemoteProgress):
    def __init__(
        self,
        progressbar: "GitRichProgress",
        task: progress.TaskID | None,
        text: str,
    ):
        super().__init__()
        self.progressbar = progressbar
        self.task = task
        self.text = text

    def update(
        self,
        op_code: int,
        cur_count: str | float,
        max_count: float | str | None = None,
        message: str | None = "",
    ) -> None:
        with self.progressbar.lock:
            if max_count is None:
                max_count = 100
            cur_count = int(float(cur_count) / float(max_count) * 100)
            max_count = 100

            if self.task is None:
                self.progressbar.log(
                    f"{self.text}: {cur_count}/{max_count} ({message})"
                )
            else:
                self.progressbar.progressbar.update(
                    task_id=self.task,
                    completed=float(cur_count),
                    total=float(max_count),
                    message=message,
                )

    def stop(self) -> None:
        if self.task:
            self.progressbar.progressbar.stop_task(self.task)
            self.progressbar.progressbar.remove_task(self.task)


class GitRichProgress:
    max_name_length = 20

    def __init__(self, lock: RLock) -> None:
        super().__init__()

        self.lock = lock
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

    def task(self, name: str, desc: str) -> GitRemoteProgress:
        with self.lock:
            if Console().is_terminal:
                if len(name) > GitRichProgress.max_name_length - 3:
                    idx = -1 * (GitRichProgress.max_name_length - 3)
                    name = f"...{name[idx:]}"
                name_format = "{0: <%s}" % GitRichProgress.max_name_length
                name = name_format.format(name)
                text = f"[yellow]({desc})[/] {name}"

                task = self.progressbar.add_task(
                    description=text,
                    total=100.0,
                    message="",
                )
            else:
                task = None
                text = f"({desc}) {name}"
            return GitRemoteProgress(self, task, text)

    def log(self, msg: str) -> None:
        self.progressbar.print(msg, justify="left")


class GitAction(Protocol):
    def run(
        self,
        progress: GitRichProgress,
        verbose: bool = False,
        dry_run: bool = False,
    ) -> None:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def desc(self) -> str:
        ...

    @property
    def server(self) -> str:
        ...


@dataclass(frozen=True, eq=True)
class GitCloneAction(GitAction):
    base_url: str
    delimiter: str
    remote_src: str
    full_url: str
    dest: str
    branch: str | None = None

    def run(
        self,
        progress: GitRichProgress,
        verbose: bool = False,
        dry_run: bool = False,
    ) -> None:
        dest_path = Path(self.dest)
        parent_dir = dest_path.parents[0]

        env = dict(GIT_TERMINAL_PROMPT="0")

        if not dest_path.exists():
            if verbose or not Console().is_terminal:
                progress.log(
                    f"[green]Repository Clone[/] [blue]'{self.dest}'[/]"
                )
            if not dry_run:
                task: GitRemoteProgress | None = None
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)

                    task = progress.task(self.name, self.desc)
                    Repo.clone_from(  # type: ignore
                        url=self.full_url,
                        to_path=Path(self.dest).resolve(),
                        progress=task,  # type: ignore
                        env=env,
                        branch=self.branch,
                        multi_options=["--recurse-submodules"],
                    )
                except Exception as e:
                    try:
                        if task:
                            task.stop()
                    except Exception:
                        pass
                    raise e
        elif verbose:
            progress.log(
                f"[yellow]Repository Clone[/] [blue]'{self.dest}'[/]"
                " [yellow]Directory does already exist[/]"
            )

    @property
    def name(self) -> str:
        return self.dest

    @property
    def desc(self) -> str:
        return "Clone"

    @property
    def server(self) -> str:
        return self.base_url


class ClonePerServerHandler:
    def __init__(
        self,
        actions: list[GitAction] = [],
        max_connections_per_server: int = 5,
        max_connections_total: int = 5,
    ) -> None:
        self.max_connections_per_server = max_connections_per_server
        self.max_connections_total = max_connections_total

        self.actions: list[GitAction] = []
        self.cur_actions: dict[str, int] = {}
        self.cur_total_actions: int = 0

        for action in actions:
            self.add_action(action)

    def add_action(self, action: GitAction) -> None:
        if action.server not in self.cur_actions:
            self.cur_actions[action.server] = 0
        self.actions.append(action)

    def _get_next_action(self) -> GitAction | None:
        for action in self.actions:
            if (
                self.cur_actions[action.server]
                < self.max_connections_per_server
                and self.cur_total_actions < self.max_connections_total
            ):
                return action
        return None

    def _run_action(
        self,
        pool: ThreadPool,
        lock: RLock,
        action: GitAction,
        errors: list[tuple[GitAction, BaseException]],
        gitrichprogress: GitRichProgress,
        verbose: bool,
        dry_run: bool,
    ) -> None:
        def callback(res: None) -> None:
            with lock:
                self.cur_actions[action.server] -= 1
                self.cur_total_actions -= 1

        def error_callback(exc: BaseException) -> None:
            with lock:
                errors.append((action, exc))
                callback(None)

        with lock:
            self.cur_actions[action.server] += 1
            self.cur_total_actions += 1
            self.actions.remove(action)
            pool.apply_async(
                func=action.run,
                args=(gitrichprogress, verbose, dry_run),
                callback=callback,
                error_callback=error_callback,
            )

    def run(self, verbose: bool = False, dry_run: bool = False) -> None:
        lock = RLock()

        gitrichprogress = GitRichProgress(lock)

        errors: list[tuple[GitAction, BaseException]] = []

        with ThreadPool(self.max_connections_total) as pool:
            while True:
                with lock:
                    action = self._get_next_action()
                if action:
                    self._run_action(
                        pool,
                        lock,
                        action,
                        errors,
                        gitrichprogress,
                        verbose,
                        dry_run,
                    )
                else:
                    time.sleep(0.2)
                with lock:
                    if not self.cur_total_actions and not self.actions:
                        break
        self.cur_actions = {}
        self.cur_total_actions = 0

        error_strs: list[str] = []
        for a, e in errors:
            error_strs.append(
                f"[bold]Error:[/] {a.desc}: {a.name} -> {str(e)}"
            )
        if error_strs:
            error_strs = [
                f"The following git error{'s' if len(errors)>1 else''}"
                " occurred:"
            ] + error_strs
            raise GitOperationException("\n".join(error_strs))
