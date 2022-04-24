import os
from typing import Any

from pydantic import ValidationError, root_validator, validator
from pydantic_yaml import YamlModel

from gitclone.exceptions import GitConfigurationException


class BaseConfig(YamlModel):
    @root_validator(pre=True)
    def check_model(cls, values: dict[str, Any]) -> dict[str, Any]:
        for k, _ in values.items():
            if k not in cls.__fields__.keys():
                raise ValueError(
                    f"Field '{k}' is not allowed in"
                    f" '{cls.__name__}'"  # type: ignore
                )
        return values


class GithubAutofetchConfig(BaseConfig):
    user: str
    method: str = "https"
    token: str | None = None
    private: bool = False
    path: str = "{repo}"
    includes: list[str] = []
    excludes: list[str] = []

    @validator("method")
    def validate_method(cls, v: str) -> str:
        expected = ["ssh", "https"]
        if v not in expected:
            raise ValueError(f"Method '{v}' not supported.")
        return v

    @validator("path")
    def validate_path(cls, v: str) -> str:
        if not v:
            raise ValueError("Empty path given.")
        return v


class AuofetchConfig(BaseConfig):
    github: GithubAutofetchConfig | None = None


class TextConfig(BaseConfig):
    repositories: list[str] = []

    @classmethod
    def from_path(cls, path: str) -> "TextConfig":
        with open(path, "r") as f:
            return cls(
                repositories=[
                    line.strip()
                    for line in f.read().strip().split(os.linesep)
                    if line.strip()
                ]
            )


class Config(BaseConfig):
    dest: str = "."
    autofetch: list[AuofetchConfig] = []
    repositories: list[str] = []

    @classmethod
    def from_path(cls, path: str) -> "Config":
        try:
            with open(path, "r") as f:
                return cls.parse_raw(f.read())  # type: ignore
        except ValidationError as e:
            raise GitConfigurationException(e)


class GlobalConfig(BaseConfig):
    config: Config = Config()
    textconfig: TextConfig = TextConfig()
