from datetime import datetime

import pytest

from conftest import touch
from tidydir.config import parse_config
from tidydir.planner import PlanError, build_plan


def targets(plan, root):
    return {m.source.name: m.target.relative_to(root.resolve()).as_posix() for m in plan.moves}


def test_files_go_to_first_matching_rule(tmp_path, config):
    touch(tmp_path / "a.jpg")
    touch(tmp_path / "b.pdf", mtime=datetime(2023, 5, 1).timestamp())
    touch(tmp_path / "notes.txt")
    plan = build_plan(tmp_path, config)
    assert targets(plan, tmp_path) == {"a.jpg": "Images/a.jpg", "b.pdf": "Docs/2023/b.pdf"}


def test_planning_changes_nothing(tmp_path, config):
    touch(tmp_path / "a.jpg")
    build_plan(tmp_path, config)
    assert (tmp_path / "a.jpg").exists()
    assert not (tmp_path / "Images").exists()


def test_hidden_files_config_and_folders_are_left_alone(tmp_path, config):
    touch(tmp_path / ".hidden.jpg")
    touch(tmp_path / "tidydir.toml")
    touch(tmp_path / "album.jpg" / "inner.jpg")  # a folder that looks like an image
    assert build_plan(tmp_path, config).moves == []


def test_include_hidden(tmp_path):
    config = parse_config(
        "[settings]\ninclude_hidden = true\n[[rule]]\nextensions = ['jpg']\ndestination = 'I'\n"
    )
    touch(tmp_path / ".hidden.jpg")
    assert targets(build_plan(tmp_path, config), tmp_path) == {".hidden.jpg": "I/.hidden.jpg"}


def test_name_clash_gets_a_number(tmp_path, config):
    touch(tmp_path / "Images" / "a.jpg")
    touch(tmp_path / "Images" / "a (1).jpg")
    touch(tmp_path / "a.jpg")
    assert targets(build_plan(tmp_path, config), tmp_path) == {"a.jpg": "Images/a (2).jpg"}


def test_name_clash_can_be_skipped(tmp_path):
    config = parse_config(
        "[settings]\non_conflict = 'skip'\n[[rule]]\nextensions = ['jpg']\ndestination = 'I'\n"
    )
    touch(tmp_path / "I" / "a.jpg")
    touch(tmp_path / "a.jpg")
    plan = build_plan(tmp_path, config)
    assert plan.moves == []
    assert [p.name for p, _ in plan.skipped] == ["a.jpg"]


def test_two_files_planned_into_the_same_name(tmp_path):
    config = parse_config("[[rule]]\ndestination = 'All/{ext}'\n")
    touch(tmp_path / "x.txt")
    touch(tmp_path / "All" / "txt" / "y.txt")
    touch(tmp_path / "y.txt")
    assert targets(build_plan(tmp_path, config), tmp_path) == {
        "x.txt": "All/txt/x.txt",
        "y.txt": "All/txt/y (1).txt",
    }


def test_destination_dot_leaves_file_in_place(tmp_path):
    config = parse_config("[[rule]]\nextensions = ['jpg']\ndestination = '.'\n")
    touch(tmp_path / "a.jpg")
    assert build_plan(tmp_path, config).moves == []


def test_rule_name_cannot_escape_the_folder(tmp_path):
    config = parse_config("[[rule]]\nname = '..'\ndestination = '{rule}'\n")
    touch(tmp_path / "a.jpg")
    with pytest.raises(PlanError):
        build_plan(tmp_path, config)
