from pathlib import Path

import pytest

from lrucheck.config import Config, ConfigError, find_pyproject, load_config


@pytest.fixture
def write_pyproject(tmp_path: Path):
    def _write(content: str) -> Path:
        target = tmp_path / "pyproject.toml"
        target.write_text(content, encoding="utf-8")
        return target

    return _write


def test_find_pyproject_in_current_directory(write_pyproject, tmp_path: Path):
    pyproject = write_pyproject("[tool.lrucheck]\n")

    found = find_pyproject(tmp_path)

    assert found == pyproject


def test_find_pyproject_walks_up_from_subdirectory(write_pyproject, tmp_path: Path):
    pyproject = write_pyproject("[tool.lrucheck]\n")
    nested = tmp_path / "src" / "pkg"
    nested.mkdir(parents=True)

    found = find_pyproject(nested)

    assert found == pyproject


def test_find_pyproject_returns_none_when_missing(tmp_path: Path):
    nested = tmp_path / "deep" / "nesting"
    nested.mkdir(parents=True)

    found = find_pyproject(nested)

    assert found is None


def test_load_config_returns_empty_when_no_pyproject(tmp_path: Path):
    config = load_config(tmp_path)

    assert config == Config()


def test_load_config_returns_empty_when_section_missing(write_pyproject, tmp_path: Path):
    write_pyproject("[project]\nname = 'demo'\n")

    config = load_config(tmp_path)

    assert config == Config()


def test_load_config_reads_ignore_list(write_pyproject, tmp_path: Path):
    write_pyproject('[tool.lrucheck]\nignore = ["LRU003", "LRU004"]\n')

    config = load_config(tmp_path)

    assert config.ignore == frozenset({"LRU003", "LRU004"})


def test_load_config_normalizes_ignore_to_uppercase(write_pyproject, tmp_path: Path):
    write_pyproject('[tool.lrucheck]\nignore = ["lru003", "Lru004"]\n')

    config = load_config(tmp_path)

    assert config.ignore == frozenset({"LRU003", "LRU004"})


def test_load_config_rejects_unknown_key(write_pyproject, tmp_path: Path):
    write_pyproject("[tool.lrucheck]\nbogus = true\n")

    with pytest.raises(ConfigError, match="unknown key"):
        load_config(tmp_path)


def test_load_config_rejects_non_list_ignore(write_pyproject, tmp_path: Path):
    write_pyproject('[tool.lrucheck]\nignore = "LRU001"\n')

    with pytest.raises(ConfigError, match="must be a list"):
        load_config(tmp_path)


def test_load_config_rejects_non_string_ignore_entry(write_pyproject, tmp_path: Path):
    write_pyproject("[tool.lrucheck]\nignore = [1, 2]\n")

    with pytest.raises(ConfigError, match="must be strings"):
        load_config(tmp_path)


def test_load_config_rejects_malformed_toml(write_pyproject, tmp_path: Path):
    write_pyproject("[tool.lrucheck\nignore = [")

    with pytest.raises(ConfigError, match="cannot parse"):
        load_config(tmp_path)
