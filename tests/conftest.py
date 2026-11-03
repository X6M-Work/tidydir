import os
from pathlib import Path

import pytest

from tidydir.config import parse_config

SAMPLE_CONFIG = """
[[rule]]
name = "Images"
extensions = ["jpg", "png"]
destination = "Images"

[[rule]]
name = "Docs"
extensions = ["pdf"]
destination = "Docs/{year}"
"""


def touch(path: Path, content: bytes = b"x", mtime: float | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


@pytest.fixture
def config():
    return parse_config(SAMPLE_CONFIG)
