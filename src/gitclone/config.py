from pydantic import BaseModel, validator, root_validator, ValidationError
from pydantic_yaml import YamlModel


class BaseConfig(YamlModel):
    @root_validator(pre=True)
    def check_model(cls, values):
        for k, v in values.items():
            if k not in cls.__fields__.keys():
                raise ValueError(k)
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


class Config(BaseConfig):
    dest: str = "."
    autofetch: list[AuofetchConfig] = []
    repositories: list[str] = []

    @classmethod
    def from_path(cls, path):
        with open(path, "r") as f:
            return cls.from_file(f)

    @classmethod
    def from_file(cls, file):
        return cls.from_str(file.read())

    @classmethod
    def from_str(cls, s):
        return cls.parse_raw(s)
