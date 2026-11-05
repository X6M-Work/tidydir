"""Working out which files move where, without touching anything."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .config import CONFIG_FILENAME, Config
from .journal import JOURNAL_DIR
from .rules import matches_any


class PlanError(ValueError):
    """Raised when the config would move files somewhere unsafe."""


@dataclass(frozen=True)
class Move:
    source: Path
    target: Path
    rule: str


@dataclass
class Plan:
    moves: list[Move] = field(default_factory=list)
    skipped: list[tuple[Path, str]] = field(default_factory=list)


def iter_candidates(
    root: Path, include_hidden: bool, exclude: tuple[str, ...] = ()
) -> Iterator[Path]:
    """Regular files directly inside ``root`` that tidydir may move."""
    for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if entry.name in (CONFIG_FILENAME, JOURNAL_DIR):
            continue
        if not include_hidden and entry.name.startswith("."):
            continue
        if exclude and matches_any(entry.name, exclude):
            continue
        if entry.is_symlink() or not entry.is_file():
            continue
        yield entry


def build_plan(root: Path, config: Config, now: float | None = None) -> Plan:
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")
    now = time.time() if now is None else now
    claimed: set[str] = set()
    plan = Plan()

    for path in iter_candidates(root, config.settings.include_hidden, config.settings.exclude):
        info = path.stat()
        rule = next(
            (r for r in config.rules if r.matches(path.name, info.st_size, info.st_mtime, now)),
            None,
        )
        if rule is None:
            continue
        folder = root.joinpath(*rule.render(path.name, info.st_mtime).parts).resolve()
        if folder != root and root not in folder.parents:
            raise PlanError(f"rule {rule.name!r} would move {path.name} outside {root}")
        if folder == root:
            continue

        target = folder / path.name
        if _taken(target, claimed):
            if config.settings.on_conflict == "skip":
                plan.skipped.append((path, f"{target.relative_to(root).as_posix()} exists"))
                continue
            target = _numbered(target, claimed)
        claimed.add(_key(target))
        plan.moves.append(Move(path, target, rule.name))

    return plan


def _key(path: Path) -> str:
    return os.path.normcase(str(path))


def _taken(path: Path, claimed: set[str]) -> bool:
    return path.exists() or _key(path) in claimed


def _numbered(target: Path, claimed: set[str]) -> Path:
    n = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({n}){target.suffix}")
        if not _taken(candidate, claimed):
            return candidate
        n += 1
