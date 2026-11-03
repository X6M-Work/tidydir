# Roadmap

Where tidydir is going. The aim: a folder organizer you can **leave running and trust**: it sorts
files as they arrive, never loses anything, and every action can be explained and undone.

Sizes are rough guesses (S = a few hours, M = about a day, L = several days, XL = a week or more).
Order may change based on feedback; each item has a matching GitHub issue.

## ✅ v0.1: foundation (released)

- Rules by extension, glob, regex, size and age, with date/extension placeholders
- `plan` / `run` / `undo` / `history`, never overwriting, journal that survives partial runs
- Built-in default rules, CI on Windows, macOS and Linux

## v0.2: a richer rule engine

- [ ] **Boolean logic in rules**: `any`/`all`/`not` groups instead of "every condition must match" (M)
- [ ] **Exclusions**: `exclude = ["*.part", "*.crdownload", "*.tmp"]` globally and per rule (S)
- [ ] **Rename templates**: `rename = "{year}-{month}-{day} {stem}{suffix}"` with slug/lowercase filters (M)
- [ ] **`tidydir check` and `tidydir explain FILE`**: validate a config, and show which rule a file hits and why the others didn't (M)
- [ ] **Error messages with line numbers** pointing into `tidydir.toml` (M)
- [ ] **`plan --json`**: stable, documented output for scripts and other tools (S)
- [ ] **User-level config** in the platform config folder (`~/.config`, `%APPDATA%`, `~/Library/Application Support`) (S)

## v0.3: actions beyond "move"

- [ ] **Per-rule actions**: `move`, `copy`, `link` and `trash` (M)
- [ ] **Cross-platform recycle bin**: Windows `IFileOperation`/shell API, macOS `NSFileManager.trashItem`, freedesktop.org Trash spec on Linux, with **no hard deletes, ever** (L)
- [ ] **Duplicate detection**: size, then partial hash, then full BLAKE2 hash so large folders stay fast, with a persistent hash cache and a `duplicates` action (L)
- [ ] **Content-aware matching**: MIME sniffing by magic bytes (catches `.pdf` files that are really HTML), EXIF date for photos (M)

## v0.4: crash-safe by design

- [ ] **Transactional runs**: write intent to the journal *before* each move, so a crash or power cut mid-run can be detected and rolled back with `tidydir recover` (L)
- [ ] **Cross-device moves**: copy, verify by hash, then remove, with progress for large files (M)
- [ ] **Undo any run** (`undo --run ID`), not just the latest, with dependency checks between runs (M)
- [ ] **Journal compaction and retention** settings (S)
- [ ] **Property-based tests** (Hypothesis): no two files ever get the same target; run + undo always restores the original tree (M)

## v0.5: hands-off mode

- [ ] **`tidydir watch`**: native file-system events (ReadDirectoryChangesW / FSEvents / inotify) with a polling fallback (L)
- [ ] **Settle detection**: wait until a download has finished growing and isn't locked before touching it (M)
- [ ] **Run as a background service**: Windows Task Scheduler / service, macOS launchd agent, systemd user unit, installed by `tidydir service install` (L)
- [ ] **Desktop notifications** summarising what was sorted, with an "undo" hint (M)

## v0.6: interactive review

- [ ] **Terminal UI** (`tidydir review`): browse the plan, untick files, change a file's destination, and preview rule edits live before running (XL)
- [ ] **Coloured, aligned output** plus `--quiet` / `--verbose` (S)
- [ ] **Shell completions** for bash, zsh, fish and PowerShell (S)

## v1.0: ecosystem and stable release

- [ ] **Plugin API** for third-party conditions and actions (entry points), with a versioned, documented interface (L)
- [ ] **Recursive mode** that understands its own destination folders and never re-sorts them (M)
- [ ] **Performance**: benchmark suite on 100k-file folders; parallel stat and hash where it helps (M)
- [ ] **Distribution**: PyPI with trusted publishing, Homebrew, winget, Scoop, and standalone binaries built in CI (L)
- [ ] **Documentation site** with a rules cookbook and recipes (Downloads, scans, camera imports, screenshots) (M)
- [ ] **Stable config format**: a v1 schema plus a migration command for older configs (M)

## Ongoing quality

- [ ] Type-checking (mypy, strict) and linting (ruff) in CI
- [ ] Coverage reporting with a minimum threshold
- [ ] Windows edge cases: long paths, locked files, case-only renames, reserved names (`CON`, `NUL`)
- [ ] Security review: symlink and junction races, never following links outside the sorted folder
