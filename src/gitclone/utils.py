from rich import print


def rpartition(s: str, d: str) -> tuple[str, str]:
    res = s.rpartition(d)
    if res[0]:
        return (res[0], res[2])
    return (res[2], res[0])


__all__ = ["print", "rpartition"]
