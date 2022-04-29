from typing import Any

import pytest

import gitclone


@pytest.fixture(autouse=True)
def add_imports(doctest_namespace: dict[str, Any]):
    doctest_namespace["gc"] = gitclone
