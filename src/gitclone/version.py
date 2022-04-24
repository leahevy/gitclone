import pkgutil

__VERSION__ = pkgutil.get_data(__name__, "VERSION").decode("utf-8").strip()

_version_list = __VERSION__.split(".")

__MAJOR_VERSION__ = int(_version_list[0])
__MINOR_VERSION__ = int(_version_list[1])
__PATCH_VERSION__ = int(_version_list[2])
