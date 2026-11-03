import pytest

from tidydir.config import CONFIG_FILENAME, DEFAULT_CONFIG, ConfigError, find_config, parse_config


def test_default_config_is_valid():
    config = parse_config(DEFAULT_CONFIG)
    assert config.rules[0].name == "Images"
    assert config.settings.on_conflict == "rename"
    assert config.settings.include_hidden is False
    assert config.source is None


def test_settings_are_read():
    config = parse_config(
        '[settings]\ninclude_hidden = true\non_conflict = "skip"\n[[rule]]\ndestination = "x"\n'
    )
    assert config.settings.include_hidden is True
    assert config.settings.on_conflict == "skip"


@pytest.mark.parametrize(
    "text, message",
    [
        ("[[rule]]\ndestination = 'x'\n[extra]\n", "unknown section"),
        ("[settings]\ncolour = 1\n[[rule]]\ndestination = 'x'\n", "unknown setting"),
        ("[settings]\non_conflict = 'overwrite'\n[[rule]]\ndestination = 'x'\n", "on_conflict"),
        ("[settings]\ninclude_hidden = 'yes'\n[[rule]]\ndestination = 'x'\n", "include_hidden"),
        ("", "no rules"),
        ("rule = 'x'\n", r"\[\[rule\]\]"),
        ("[rule]\ndestination = 'x'\n", r"\[\[rule\]\]"),
        ("[[rule]\n", "built-in config"),
        ("[[rule]]\nname = 'Pics'\n", "Pics"),
    ],
)
def test_invalid_configs(text, message):
    with pytest.raises(ConfigError, match=message):
        parse_config(text)


def test_find_config_falls_back_to_defaults(tmp_path):
    assert find_config(tmp_path).source is None


def test_find_config_prefers_folder_config(tmp_path):
    path = tmp_path / CONFIG_FILENAME
    path.write_text("[[rule]]\ndestination = 'x'\n", encoding="utf-8")
    assert find_config(tmp_path).source == path


def test_find_config_explicit_path(tmp_path):
    path = tmp_path / "custom.toml"
    path.write_text("[[rule]]\ndestination = 'y'\n", encoding="utf-8")
    assert find_config(tmp_path, path).rules[0].destination == "y"


def test_missing_explicit_config(tmp_path):
    with pytest.raises(ConfigError, match="cannot read"):
        find_config(tmp_path, tmp_path / "missing.toml")
