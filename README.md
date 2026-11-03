# tidydir

[![CI](https://github.com/zeexduaa/tidydir/actions/workflows/ci.yml/badge.svg)](https://github.com/zeexduaa/tidydir/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**Sort a messy folder into tidy subfolders using simple rules, with a preview first and an undo after.**

My Downloads folder fills up with screenshots, PDFs, installers and zip files faster than I clean it.
`tidydir` is a small command-line tool that sorts a folder for you using rules you write in a TOML
file, such as "images go to `Images/<year>`" or "installers older than 30 days go to `Installers/Old`".
It always shows you the plan before moving anything and keeps a journal, so every run can be undone.

- **Who it's for:** anyone with a cluttered Downloads, Desktop or scans folder who's comfortable with a terminal.
- **Built with:** Python 3.11+ standard library only (no dependencies), `pytest` for tests, GitHub Actions CI on Linux, macOS and Windows.

## Install

From the repository (until the first PyPI release):

```bash
pip install git+https://github.com/zeexduaa/tidydir.git
```

Or for development:

```bash
git clone https://github.com/zeexduaa/tidydir.git
cd tidydir
pip install -e ".[dev]"
```

## Quick start

```bash
cd ~/Downloads
tidydir plan          # preview: what would move where (nothing changes)
tidydir run           # do it (asks for confirmation; -y to skip)
tidydir undo          # changed your mind? put everything back
```

Example output:

```text
$ tidydir plan
  invoice-2025.pdf  ->  Documents/pdf/invoice-2025.pdf   [Documents]
  Screenshot 2026-01-01.png  ->  Images/2026/Screenshot 2026-01-01.png   [Images]
  setup.exe  ->  Installers/setup.exe   [Installers]
  song.mp3  ->  Audio/song.mp3   [Audio]

4 file(s) would move. Nothing has been changed yet.
```

Without a config file, tidydir uses sensible built-in rules (images, documents, audio, video,
archives, installers). To customise them:

```bash
tidydir init          # writes tidydir.toml into the folder; edit it to taste
```

## Commands

| Command | What it does |
| --- | --- |
| `tidydir init [DIR]` | Write a starter `tidydir.toml` (`--force` to overwrite) |
| `tidydir plan [DIR]` | Show what would move, without moving anything |
| `tidydir run [DIR]` | Move the files (`-y` skips the confirmation) |
| `tidydir undo [DIR]` | Move the files from the most recent run back |
| `tidydir history [DIR]` | List recorded runs that can be undone |

`plan` and `run` accept `-c/--config PATH` to use a config stored elsewhere.
`DIR` defaults to the current folder.

## Writing rules

Rules live in `tidydir.toml` in the folder being sorted. They are checked **top to bottom and the
first match wins**. Files that match no rule are left alone.

```toml
[settings]
include_hidden = false   # also sort files starting with "."
on_conflict = "rename"   # "rename" -> "photo (1).jpg", or "skip"

[[rule]]
name = "Screenshots"
glob = "screenshot*"
extensions = ["png", "jpg"]
destination = "Images/Screenshots/{year}-{month}"

[[rule]]
name = "Old installers"
extensions = ["exe", "msi", "dmg"]
older_than = "30d"
destination = "Installers/Old"
```

**Conditions** (all optional; every condition you give must match):

| Key | Example | Meaning |
| --- | --- | --- |
| `extensions` | `["jpg", "png"]` | File extension, case-insensitive |
| `glob` | `"invoice*"` | Shell-style name pattern, case-insensitive |
| `regex` | `"\\d{4}"` | Python regular expression searched in the name |
| `min_size` / `max_size` | `"500MB"` | Size limits (B, KB, MB, GB, TB) |
| `older_than` / `newer_than` | `"30d"` | Age by modification time (s, m, h, d, w) |

**Destination placeholders:** `{ext}`, `{year}`, `{month}`, `{day}` (from the file's modification
time) and `{rule}` (the rule's name). Destinations must stay inside the folder being sorted:
absolute paths and `..` are rejected.

See [`examples/downloads.toml`](examples/downloads.toml) for a fuller example.

## Safety

- `plan` never touches your files.
- tidydir never overwrites: name clashes get a number or are skipped.
- Only files directly inside the folder are moved. Subfolders, symlinks, hidden files (by default)
  and `tidydir.toml` itself are left alone.
- Every run is recorded in `.tidydir/history.jsonl`; `tidydir undo` reverses the latest run and
  refuses to overwrite anything that has appeared since.

## Where it's going

tidydir is at v0.1: a safe, rule-based sorter you run by hand. The goal is an organizer you can
**leave running and trust**:

- **Hands-off:** `tidydir watch` sorts new files as they finish downloading, and can run as a background service on Windows, macOS and Linux.
- **Smarter rules:** any/all/not logic, rename templates, content-aware matching (real file type, photo EXIF dates) and `tidydir explain` to show why a file went where it did.
- **More actions:** copy, link, send to the system recycle bin (never hard-delete) and fast duplicate detection.
- **Crash-safe:** transactional runs that can recover after a crash, and undo for any past run.
- **Interactive review:** a terminal UI to check and adjust the plan before anything moves.

The full plan, milestone by milestone, is in [ROADMAP.md](ROADMAP.md) and tracked in the
[issues](https://github.com/zeexduaa/tidydir/issues).

## Contributing

Bug reports and ideas are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2026 Syed Ali
