import importlib
import inspect

import pkg_resources
from typer import Typer

from gitclone.exceptions import GitExtensionException

from .extension import Extension


def load_extension_package(
    cli: Typer, ext: pkg_resources.Distribution, registered_commands: list[str]
) -> None:
    try:
        ext_module = importlib.import_module(
            ext.project_name.lower().replace("-", "_")
        )
    except ModuleNotFoundError:
        raise GitExtensionException(
            f"Extension {ext.project_name} could not be loaded:"
            f" Module not found ({ext.project_name})"
        )
    for k, v in vars(ext_module).items():
        if inspect.isclass(v):
            if issubclass(v, Extension) and v != Extension:
                try:
                    ext_obj = v()  # type: ignore
                except Exception:
                    raise GitExtensionException(
                        f"Extension {ext.project_name} could not be loaded"
                        f" (class {k})\n  Extension init failed"
                    )

                if ext_obj.command is None or not ext_obj.command_name:
                    raise GitExtensionException(
                        f"Extension {ext.project_name} could not be"
                        f" loaded (class {k})\n Extension does"
                        " not provide the required properties"
                    )
                elif ext_obj.command_name in registered_commands:
                    raise GitExtensionException(
                        f"Extension {ext.project_name}: Command"
                        f" {ext_obj.command_name} is already registered"
                    )
                try:
                    cli.add_typer(ext_obj.command, name=ext_obj.command_name)
                except Exception:
                    raise GitExtensionException(
                        f"Extension {ext.project_name} could not be loaded"
                        " (class {k}): Error adding command to typer"
                    )


def load_extensions(cli: Typer, registered_commands: list[str]) -> None:
    installed_packages = pkg_resources.working_set
    for i in installed_packages:
        if i.project_name.startswith("pygitclone-"):
            load_extension_package(cli, i, registered_commands)


__all__ = ["load_extensions"]
