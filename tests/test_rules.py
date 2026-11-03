from datetime import datetime
from pathlib import PurePosixPath

import pytest

from tidydir.rules import Rule, RuleError, file_extension, parse_age, parse_size


def make(**data):
    data.setdefault("destination", "Out")
    return Rule.from_dict(data, 1)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0),
        (512, 512),
        ("512", 512),
        ("1KB", 1024),
        ("1.5 mb", int(1.5 * 1024**2)),
        ("2G", 2 * 1024**3),
    ],
)
def test_parse_size(value, expected):
    assert parse_size(value) == expected


@pytest.mark.parametrize("value", ["", "abc", "5 parsecs", -1, True])
def test_parse_size_rejects_nonsense(value):
    with pytest.raises(RuleError):
        parse_size(value)


def test_parse_age():
    assert parse_age("30d") == 30 * 86400
    assert parse_age("2w") == 14 * 86400
    assert parse_age("12H") == 12 * 3600


@pytest.mark.parametrize("value", ["1y", "soon", ""])
def test_parse_age_rejects_nonsense(value):
    with pytest.raises(RuleError):
        parse_age(value)


@pytest.mark.parametrize(
    "name, ext",
    [("Photo.JPG", "jpg"), ("archive.tar.gz", "gz"), (".bashrc", ""), ("README", "")],
)
def test_file_extension(name, ext):
    assert file_extension(name) == ext


def test_extensions_are_case_insensitive():
    rule = make(extensions=[".PNG", "jpg"])
    assert rule.matches("a.png", 1, 0, 0)
    assert rule.matches("b.JPG", 1, 0, 0)
    assert not rule.matches("c.gif", 1, 0, 0)


def test_glob_and_regex_must_both_match():
    rule = make(glob="invoice*", regex=r"\d{4}")
    assert rule.matches("Invoice-2024.pdf", 1, 0, 0)
    assert not rule.matches("invoice-draft.pdf", 1, 0, 0)
    assert not rule.matches("receipt-2024.pdf", 1, 0, 0)


def test_size_bounds_are_inclusive():
    rule = make(min_size="1KB", max_size="2KB")
    assert not rule.matches("f", 1023, 0, 0)
    assert rule.matches("f", 1024, 0, 0)
    assert rule.matches("f", 2048, 0, 0)
    assert not rule.matches("f", 2049, 0, 0)


def test_age_bounds():
    now = 1_000_000
    old = make(older_than="1d")
    assert old.matches("f", 1, now - 86400, now)
    assert not old.matches("f", 1, now - 100, now)
    fresh = make(newer_than="1h")
    assert fresh.matches("f", 1, now - 60, now)
    assert not fresh.matches("f", 1, now - 7200, now)


def test_rule_without_conditions_matches_everything():
    assert make().matches("anything.xyz", 123, 0, 0)


def test_render_placeholders():
    rule = make(name="Pics", destination="{rule}/{year}/{month}/{ext}")
    mtime = datetime(2024, 3, 9, 12).timestamp()
    assert rule.render("x.PNG", mtime) == PurePosixPath("Pics/2024/03/png")


def test_render_without_extension():
    assert make(destination="{ext}").render("Makefile", 0) == PurePosixPath("noext")


def test_backslashes_in_destination_are_normalised():
    assert make(destination="A\\B").destination == "A/B"


@pytest.mark.parametrize(
    "destination", ["/abs", "../up", "a/../../b", "C:/x", "{nope}", "{}", "{year", "  "]
)
def test_unsafe_or_broken_destinations_are_rejected(destination):
    with pytest.raises(RuleError):
        make(destination=destination)


def test_typo_in_key_is_reported():
    with pytest.raises(RuleError, match="extention"):
        make(extention=["jpg"])


def test_bad_regex_is_reported():
    with pytest.raises(RuleError, match="regex"):
        make(regex="(")


def test_destination_is_required():
    with pytest.raises(RuleError, match="destination"):
        Rule.from_dict({"name": "x"}, 1)


def test_bad_size_names_the_rule():
    with pytest.raises(RuleError, match="Big"):
        make(name="Big", min_size="huge")
