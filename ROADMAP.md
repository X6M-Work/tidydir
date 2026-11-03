# Roadmap

Rough plan for tidydir. Sizes are guesses; order may change based on feedback.

## v0.2: more ways to match and act

- [ ] **`tidydir check`**: validate a config and explain each rule in plain words (S)
- [ ] **`plan --json`**: machine-readable plan output for scripting (S)
- [ ] **Per-rule actions**: `action = "move" | "copy" | "trash"` (trash via the OS recycle bin, never hard delete) (M)
- [ ] **Rename templates**: `rename = "{year}-{month}-{day} {stem}{suffix}"` (M)
- [ ] **Duplicate detection**: hash identical files and send extra copies to a `Duplicates/` folder (M)
- [ ] **User-level config**: fall back to `~/.config/tidydir/config.toml` (or `%APPDATA%` on Windows) (S)

## v0.3: bigger folders

- [ ] **Recursive mode** (`--recursive`) that skips the rules' own destination folders (M)
- [ ] **Ignore list**: `exclude = ["*.part", "*.crdownload"]` so in-progress downloads aren't touched (S)
- [ ] **Watch mode** (`tidydir watch`): poll the folder and sort new files as they settle (L)
- [ ] Guide for scheduled runs with cron, launchd and Windows Task Scheduler (S)

## v0.4: polish and release

- [ ] **Undo a specific run** (`tidydir undo --run ID`) and history pruning (M)
- [ ] Coloured, aligned output with a `--quiet` flag (S)
- [ ] Shell completions for bash, zsh, fish and PowerShell (S)
- [ ] Publish to PyPI with a release workflow on tags (S)
- [ ] Documentation site with a rules cookbook (M)

## Quality (ongoing)

- [ ] Tests for Windows edge cases: long paths, locked files, case-only renames
- [ ] Property-based tests for the planner (no two files ever get the same target)
- [ ] Linting and type-checking in CI (ruff, mypy)

S = a few hours, M = a day or so, L = several days.
