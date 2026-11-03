"""Rules decide which files move and where they go."""

from __future__ import annotations

import fnmatch
import re
import string
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any

PLACEHOLDERS = frozenset({"ext", "year", "month", "day", "rule"})

_SIZE_UNITS = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_AGE_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 7 * 86400}
_RULE_KEYS = frozenset(
    {
        "name",
        "destination",
        "extensions",
        "glob",
        "regex",
        "min_size",
        "max_size",
        "older_than",
        "newer_than",
    }
)


class RuleError(ValueError):
    """Raised when a rule in the configuration is invalid."""


def parse_size(value: Any) -> int:
    """Turn ``500``, ``"500KB"`` or ``"1.5 GB"`` into a number of bytes."""
    if isinstance(value, bool):
        raise RuleError(f"invalid size {value!r}")
    if isinstance(value, int):
        if value < 0:
            raise RuleError(f"size cannot be negative: {value}")
        return value
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([kmgt]?b?)\s*", str(value), re.IGNORECASE)
    if not match:
        raise RuleError(f"invalid size {value!r} (try '500KB' or '2GB')")
    number, unit = match.groups()
    unit = unit.upper()
    if not unit.endswith("B"):
        unit += "B"
    return int(float(number) * _SIZE_UNITS[unit])


def parse_age(value: Any) -> int:
    """Turn ``"12h"``, ``"30d"`` or ``"2w"`` into a number of seconds."""
    match = re.fullmatch(r"\s*(\d+)\s*([smhdw])\s*", str(value), re.IGNORECASE)
    if not match:
        raise RuleError(f"invalid age {value!r} (try '12h', '30d' or '2w')")
    number, unit = match.groups()
    return int(number) * _AGE_UNITS[unit.lower()]


def file_extension(filename: str) -> str:
    """Lower-case extension without the dot; ``""`` when there is none."""
    return PurePosixPath(filename).suffix.lower().lstrip(".")


def _check_destination(label: str, destination: str) -> None:
    try:
        fields = {f for _, f, _, _ in string.Formatter().parse(destination) if f is not None}
    except ValueError as exc:
        raise RuleError(f"{label}: bad destination {destination!r}: {exc}") from exc
    unknown = fields - PLACEHOLDERS
    if unknown:
        names = ", ".join("{" + f + "}" for f in sorted(unknown))
        raise RuleError(f"{label}: unknown placeholder(s) in destination: {names}")
    path = PurePosixPath(destination)
    if path.is_absolute() or re.match(r"^[A-Za-z]:", destination) or ".." in path.parts:
        raise RuleError(f"{label}: destination must be a relative folder inside the sorted directory")


def _optional(parse, value):
    return None if value is None else parse(value)


@dataclass(frozen=True)
class Rule:
    """One ``[[rule]]`` table from the config. Every condition given must match."""

    name: str
    destination: str
    extensions: frozenset[str] = frozenset()
    glob: str | None = None
    regex: re.Pattern[str] | None = None
    min_size: int | None = None
    max_size: int | None = None
    older_than: int | None = None
    newer_than: int | None = None

    @classmethod
    def from_dict(cls, data: Any, index: int) -> Rule:
        if not isinstance(data, dict):
            raise RuleError(f"rule #{index} must be a table")
        label = str(data.get("name") or f"rule #{index}")
        unknown = set(data) - _RULE_KEYS
        if unknown:
            raise RuleError(f"{label}: unknown key(s) {', '.join(sorted(unknown))}")

        destination = data.get("destination")
        if not isinstance(destination, str) or not destination.strip():
            raise RuleError(f"{label}: 'destination' is required")
        destination = destination.strip().replace("\\", "/")
        _check_destination(label, destination)

        extensions = data.get("extensions", [])
        if isinstance(extensions, str):
            extensions = [extensions]
        try:
            regex = re.compile(data["regex"]) if "regex" in data else None
        except re.error as exc:
            raise RuleError(f"{label}: invalid regex: {exc}") from exc

        try:
            return cls(
                name=label,
                destination=destination,
                extensions=frozenset(str(e).lower().lstrip(".") for e in extensions),
                glob=data.get("glob"),
                regex=regex,
                min_size=_optional(parse_size, data.get("min_size")),
                max_size=_optional(parse_size, data.get("max_size")),
                older_than=_optional(parse_age, data.get("older_than")),
                newer_than=_optional(parse_age, data.get("newer_than")),
            )
        except RuleError as exc:
            raise RuleError(f"{label}: {exc}") from exc

    def matches(self, filename: str, size: int, mtime: float, now: float) -> bool:
        if self.extensions and file_extension(filename) not in self.extensions:
            return False
        if self.glob and not fnmatch.fnmatchcase(filename.lower(), self.glob.lower()):
            return False
        if self.regex and not self.regex.search(filename):
            return False
        if self.min_size is not None and size < self.min_size:
            return False
        if self.max_size is not None and size > self.max_size:
            return False
        age = now - mtime
        if self.older_than is not None and age < self.older_than:
            return False
        if self.newer_than is not None and age > self.newer_than:
            return False
        return True

    def render(self, filename: str, mtime: float) -> PurePosixPath:
        """The folder (relative to the sorted directory) this file goes into."""
        when = datetime.fromtimestamp(mtime)
        values = {
            "ext": file_extension(filename) or "noext",
            "year": f"{when:%Y}",
            "month": f"{when:%m}",
            "day": f"{when:%d}",
            "rule": self.name.replace("/", "-").replace("\\", "-"),
        }
        return PurePosixPath(self.destination.format(**values))
