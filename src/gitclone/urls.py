import re
import urllib

from gitclone.exceptions import RepositoryFormatException
from gitclone.utils import rpartition


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
        raise RepositoryFormatException(
            f"[red]Error:[/]\n"
            f"  [red]Got invalid repository url[/] [yellow]'{repostr}'[/]\n"
            "  [red]Expected[/] [green]url[/][blue]@[/][green]branch[/] or just [green]url[/]",
            repostr,
        )

    return (baseurl, path, branch, dest)
