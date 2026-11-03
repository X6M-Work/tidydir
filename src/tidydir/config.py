"""Loading ``tidydir.toml`` configuration files."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .rules import Rule, RuleError

CONFIG_FILENAME = "tidydir.toml"
CONFLICT_POLICIES = ("rename", "skip")

DEFAULT_CONFIG = """\
# tidydir configuration
# Rules are checked top to bottom and the first match wins.
# Files that match no rule stay where they are.
#
# Conditions (all optional, every one given must match):
#   extensions = ["jpg", "png"]   glob = "invoice*"   regex = "\\\\d{4}"
#   min_size = "10MB"   max_size = "1GB"   older_than = "30d"   newer_than = "12h"
# Destination placeholders: {ext} {year} {month} {day} {rule}

[settings]
include_hidden = false   # also sort files whose name starts with "."
on_conflict = "rename"   # "rename" -> "photo (1).jpg", or "skip"

[[rule]]
name = "Images"
extensions = ["jpg", "jpeg", "png", "gif", "webp", "heic", "svg", "bmp"]
destination = "Images/{year}"

[[rule]]
name = "Documents"
extensions = ["pdf", "doc", "docx", "odt", "txt", "md", "rtf", "xls", "xlsx", "csv", "ppt", "pptx"]
destination = "Documents/{ext}"

[[rule]]
name = "Audio"
extensions = ["mp3", "wav", "flac", "ogg", "m4a"]
destination = "Audio"

[[rule]]
name = "Video"
extensions = ["mp4", "mkv", "mov", "avi", "webm"]
destination = "Video"

[[rule]]
name = "Archives"
extensions = ["zip", "rar", "7z", "tar", "gz", "bz2", "xz"]
destination = "Archives"

[[rule]]
name = "Installers"
extensions = ["exe", "msi", "dmg", "pkg", "deb", "rpm", "appimage"]
destination = "Installers"
"""


class ConfigError(ValueError):
    """Raised when a configuration file cannot be used."""


@dataclass(frozen=True)
class Settings:
    include_hidden: bool = False
    on_conflict: str = "rename"


@dataclass(frozen=True)
class Config:
    rules: tuple[Rule, ...]
    settings: Settings = field(default_factory=Settings)
    source: Path | None = None  # None means the built-in defaults


def parse_config(text: str, source: Path | None = None) -> Config:
    where = str(source) if source else "built-in config"
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{where}: {exc}") from exc

    unknown = set(data) - {"settings", "rule"}
    if unknown:
        raise ConfigError(f"{where}: unknown section(s) {', '.join(sorted(unknown))}")

    raw_settings = data.get("settings", {})
    if not isinstance(raw_settings, dict):
        raise ConfigError(f"{where}: [settings] must be a table")
    unknown = set(raw_settings) - {"include_hidden", "on_conflict"}
    if unknown:
        raise ConfigError(f"{where}: unknown setting(s) {', '.join(sorted(unknown))}")
    include_hidden = raw_settings.get("include_hidden", False)
    if not isinstance(include_hidden, bool):
        raise ConfigError(f"{where}: include_hidden must be true or false")
    on_conflict = raw_settings.get("on_conflict", "rename")
    if on_conflict not in CONFLICT_POLICIES:
        raise ConfigError(f"{where}: on_conflict must be one of {', '.join(CONFLICT_POLICIES)}")

    raw_rules = data.get("rule", [])
    if not isinstance(raw_rules, list):
        raise ConfigError(f"{where}: rules must be written as [[rule]] tables")
    if not raw_rules:
        raise ConfigError(f"{where}: no rules defined (add a [[rule]] table)")
    try:
        rules = tuple(Rule.from_dict(raw, i) for i, raw in enumerate(raw_rules, 1))
    except RuleError as exc:
        raise ConfigError(f"{where}: {exc}") from exc

    return Config(rules, Settings(include_hidden, on_conflict), source)


def load_config(path: Path) -> Config:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc.strerror}") from exc
    return parse_config(text, path)


def find_config(directory: Path, explicit: Path | None = None) -> Config:
    """Use ``explicit`` if given, else ``DIR/tidydir.toml``, else the built-in rules."""
    if explicit is not None:
        return load_config(explicit)
    candidate = Path(directory) / CONFIG_FILENAME
    if candidate.is_file():
        return load_config(candidate)
    return parse_config(DEFAULT_CONFIG)
