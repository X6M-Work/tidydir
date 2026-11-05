import pytest

from conftest import touch
from tidydir.config import DEFAULT_CONFIG, ConfigError, parse_config
from tidydir.planner import build_plan
from tidydir.rules import Rule, RuleError


def moved(tmp_path, config):
    return sorted(m.source.name for m in build_plan(tmp_path, config).moves)


def test_global_exclude_leaves_matching_files_alone(tmp_path):
    config = parse_config(
        "[settings]\nexclude = ['*.part', '*.crdownload']\n"
        "[[rule]]\ndestination = 'Everything'\n"
    )
    for name in ("movie.mkv.part", "setup.exe.crdownload", "song.mp3"):
        touch(tmp_path / name)
    assert moved(tmp_path, config) == ["song.mp3"]


def test_global_exclude_is_case_insensitive_and_accepts_a_single_string(tmp_path):
    config = parse_config("[settings]\nexclude = '*.TMP'\n[[rule]]\ndestination = 'All'\n")
    touch(tmp_path / "scratch.tmp")
    touch(tmp_path / "keep.txt")
    assert config.settings.exclude == ("*.TMP",)
    assert moved(tmp_path, config) == ["keep.txt"]


def test_per_rule_exclude_lets_later_rules_match(tmp_path):
    config = parse_config(
        "[[rule]]\nname = 'Images'\nextensions = ['png']\nexclude = ['screenshot*']\ndestination = 'Images'\n"
        "[[rule]]\nname = 'Screens'\nglob = 'screenshot*'\ndestination = 'Screens'\n"
    )
    touch(tmp_path / "Screenshot 1.png")
    touch(tmp_path / "cat.png")
    plan = build_plan(tmp_path, config)
    assert {m.source.name: m.rule for m in plan.moves} == {
        "cat.png": "Images",
        "Screenshot 1.png": "Screens",
    }


def test_rule_exclude_in_matches():
    rule = Rule.from_dict({"destination": "x", "exclude": ["*.tmp"]}, 1)
    assert rule.exclude == ("*.tmp",)
    assert not rule.matches("a.tmp", 1, 0, 0)
    assert rule.matches("a.txt", 1, 0, 0)


@pytest.mark.parametrize("bad", [3, ["ok", 4], [""], {"a": 1}])
def test_bad_rule_exclude_is_rejected(bad):
    with pytest.raises(RuleError, match="exclude"):
        Rule.from_dict({"destination": "x", "exclude": bad}, 1)


def test_empty_exclude_list_means_no_exclusions():
    assert Rule.from_dict({"destination": "x", "exclude": []}, 1).exclude == ()


def test_bad_global_exclude_is_rejected():
    with pytest.raises(ConfigError, match=r"\[settings\] exclude"):
        parse_config("[settings]\nexclude = 5\n[[rule]]\ndestination = 'x'\n")


def test_default_config_skips_unfinished_downloads(tmp_path):
    config = parse_config(DEFAULT_CONFIG)
    touch(tmp_path / "video.mp4.part")
    touch(tmp_path / "installer.exe.crdownload")
    touch(tmp_path / "~$report.docx")
    touch(tmp_path / "photo.jpg")
    assert moved(tmp_path, config) == ["photo.jpg"]
