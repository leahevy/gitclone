import json


class GitcloneException(Exception):
    values: list[str] = []

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self._values = kwargs

        for k, v in kwargs.items():
            if hasattr(self.__class__, "values"):
                if k not in self.__class__.values:
                    raise GitcloneException(
                        f"Exception field '{k}' is not allowed.\n"
                        f"  Class: {self.__class__}\n"
                        f"  Original message: '{message}'\n"
                        f"  Data: {json.dumps(kwargs)}"
                    )
            setattr(self, k, v)

    def __str__(self) -> str:
        if not self.message:
            return json.dumps(self._values)
        else:
            return self.message


class CoreException(GitcloneException):
    pass


class RepositoryFormatException(GitcloneException):
    values = ["repostr"]
