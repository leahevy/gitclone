import pkgutil

_version_data = pkgutil.get_data(__name__, "VERSION")

if not _version_data:
    _version_data = b""

__VERSION__ = _version_data.decode("utf-8").strip()

_version_list = __VERSION__.split(".")

if not _version_list:
    _version_list = ["0", "0", "0"]

__MAJOR_VERSION__ = int(_version_list[0])
__MINOR_VERSION__ = int(_version_list[1])
__PATCH_VERSION__ = int(_version_list[2])

__all__ = [
    "__VERSION__",
    "__MAJOR_VERSION__",
    "__MINOR_VERSION__",
    "__PATCH_VERSION__",
]
