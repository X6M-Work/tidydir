# Contributing

Thanks for taking a look! Bug reports, rule ideas and pull requests are all welcome.

## Set up

```bash
git clone https://github.com/zeexduaa/tidydir.git
cd tidydir
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

## Guidelines

- Keep tidydir dependency-free (standard library only) unless there's a strong reason.
- Never add a code path that overwrites or permanently deletes user files.
- Add or update tests for any behaviour change, and note it in `CHANGELOG.md` under *Unreleased*.
- Use made-up sample files in tests and examples, never real personal data.

## Reporting bugs

Please include your OS, Python version, the command you ran, the output, and the relevant part of
your `tidydir.toml`.
