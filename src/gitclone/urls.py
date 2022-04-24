import re

from gitclone.exceptions import RepositoryFormatException
from gitclone.utils import rpartition

ssh_re = r"^([^@/]+@[^:]+):([^@]+)(?:@([^@]+))?$"
oauth_re = r"^([a-z]+://[^@/]+@[^@/]+)/([^@]+)(?:@([^@]+))?$"
normal_re = r"^([a-z]+://[^@/]+)/([^@]+)(?:@([^@]+))?$"


def parse_url(repostr):
    try:
        repostr.strip()
        url, dest = rpartition(repostr, " ")
        url = url.strip()
        dest = dest.strip()
        delimiter = "/"

        if " " in url:
            raise ValueError()

        result_ssh = re.search(ssh_re, url)
        result_oauth = re.search(oauth_re, url)
        result_normal = re.search(normal_re, url)

        if result_ssh:
            delimiter = ":"

            baseurl = result_ssh.group(1)
            path = result_ssh.group(2)
            branch = result_ssh.group(3) or ""
        elif result_oauth:
            baseurl = result_oauth.group(1)
            path = result_oauth.group(2)
            branch = result_oauth.group(3) or ""
        elif result_normal:
            baseurl = result_normal.group(1)
            path = result_normal.group(2)
            branch = result_normal.group(3) or ""
        else:
            raise ValueError()
        if not dest:
            dest = path.split("/")[-1]
            dest, _ = rpartition(dest, ".")
        fullurl = delimiter.join([baseurl, path])

        if "//" in path or "//" in dest:
            raise ValueError()
    except ValueError:
        raise RepositoryFormatException(
            f"[red]Got invalid repository url[/] [yellow]'{repostr}'[/]\n"
            "  [red]Expected[/] [green]url[/][blue]@[/][green]branch[/] [green]directory[/] or just [green]url[/] [green]directory[/] or [green]url[/]",
            repostr=repostr,
        )
    return (baseurl, delimiter, path, fullurl, branch, dest)
