import sys

from functools import wraps

from rich import print


def catch_cli_exception(
    which_exception: list[Exception] | Exception | None = Exception, exit_code: int = 1
):
    def decorator(func):
        @wraps(func)
        def exception_handled_fuction(*args: object, **kwargs: object):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not which_exception:
                    raise
                found_exc = False
                if issubclass(which_exception, list):
                    for exc_cls in which_exception:
                        if isinstance(e, exc_cls):
                            found_exc = True
                            break
                elif isinstance(e, which_exception):
                    found_exc = True
                if not found_exc:
                    raise
                if "--debug" in sys.argv or "-d" in sys.argv:
                    raise
                print(f"[red][bold]Error: [/]{str(e)}[/]")
                sys.exit(exit_code)

        return exception_handled_fuction

    return decorator
