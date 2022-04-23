import os

from pydantic import BaseModel, validator, root_validator, ValidationError
from pydantic_yaml import YamlModel

from gitclone.exceptions import GitConfigurationException


class BaseConfig(YamlModel):
    @root_validator(pre=True)
    def check_model(cls, values):
        for k, v in values.items():
            if k not in cls.__fields__.keys():
                raise ValueError(f"Field '{k}' is not allowed in '{cls.__name__}'")
        return values


class GithubAutofetchConfig(BaseConfig):
    user: str
    method: str = "https"
    token: str | None = None
    private: bool = False
    path: str = "{repo}"

    @validator("method")
    def validate_method(cls, v):
        expected = ["ssh", "https"]
        if v not in expected:
            raise ValueError(f"Method '{v}' not supported.")
        return v

    @validator("path")
    def validate_path(cls, v):
        if not v:
            raise ValueError(f"Empty path given.")
        return v


class AuofetchConfig(BaseConfig):
    github: GithubAutofetchConfig | None = None


class TextConfig(BaseConfig):
    repositories: list[str] = []

    @classmethod
    def from_path(cls, path):
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
    def from_path(cls, path):
        try:
            with open(path, "r") as f:
                return cls.parse_raw(f.read())
        except ValidationError as e:
            raise GitConfigurationException(e)


class GlobalConfig(BaseConfig):
    config: Config = Config()
    textconfig: TextConfig = TextConfig()
