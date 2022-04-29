import os
from typing import Any

from pydantic import BaseModel, ValidationError, root_validator, validator
from pydantic_yaml import YamlModelMixin

from gitclone.exceptions import GitConfigurationException
from gitclone.utils import print


class BaseConfig(YamlModelMixin, BaseModel):
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


class Config(BaseConfig):
    dest: str = "."
    autofetch: list[AuofetchConfig] = []
    repositories: list[str] | None = []

    @classmethod
    def from_path(cls, path: str) -> "Config":
        try:
            with open(path, "r") as f:
                return cls.parse_raw(f.read())  # type: ignore
        except ValidationError as e:
            raise GitConfigurationException(e)


class ConfigManager:
    DEFAULT_CONFIG = ".gitclone.yml"
    ACCEPTED_CONFIGS = [
        "gitclone.yml",
        "gitclone.yaml",
        ".gitclone.yml",
        ".gitclone.yaml",
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _find_config_in_dir(self, directory: str) -> tuple[str, bool]:
        for f in ConfigManager.ACCEPTED_CONFIGS:
            path = os.path.join(directory, f)
            if os.path.exists(path):
                return path, True
        fallback_config = os.path.join(directory, ConfigManager.DEFAULT_CONFIG)
        exists = os.path.exists(fallback_config)
        return fallback_config, exists

    def _resolve_config(
        self,
        load_global: bool,
        fallback_to_global: bool,
        global_config_directory: str | None,
        must_exist: bool,
    ) -> str | None:
        if global_config_directory is None:
            global_config_directory = os.path.join(
                os.path.expanduser("~"), ".config"
            )

        if load_global:
            config, exists = self._find_config_in_dir(global_config_directory)
            return config
        else:
            cur_dir = os.getcwd()
            config, exists = self._find_config_in_dir(cur_dir)
            if not exists:
                if fallback_to_global:
                    config, exists = self._find_config_in_dir(
                        global_config_directory
                    )
        if not exists and must_exist:
            return None
        return config

    def write_config(
        self,
        config: Config,
        to_global: bool = False,
        global_config_directory: str | None = None,
    ) -> None:
        configpath = self._resolve_config(
            load_global=to_global,
            fallback_to_global=to_global,
            global_config_directory=global_config_directory,
            must_exist=False,
        )
        raise NotImplementedError(configpath)  # TODO
        if not configpath:
            raise GitConfigurationException(
                "Gitclone configuration could not be resolved."
            )
        os.makedirs(os.path.dirname(configpath), exist_ok=True)

        with open(configpath, "w") as f:
            f.write(config.yaml())  # type: ignore

    def get_default_config(self) -> Config:
        return Config()

    def get_config(
        self,
        load_global: bool = True,
        global_config_directory: str | None = None,
        verbose: bool | None = None,
    ) -> Config:
        if verbose is None:
            verbose = self.verbose
        if global_config_directory is None:
            global_config_directory = os.path.join(
                os.path.expanduser("~"), ".config"
            )
        configpath = self._resolve_config(
            load_global=False,
            fallback_to_global=load_global,
            global_config_directory=global_config_directory,
            must_exist=True,
        )
        if not configpath:
            if verbose:
                print("[green]Using default configuration[/]")
            config = self.get_default_config()
        else:
            if verbose:
                print(
                    "[green]Reading configuration file:"
                    f" [blue]{configpath}[/][/]"
                )
            config = Config.from_path(configpath)
        return config
