from pathlib import Path

import pytest

from lrucheck.cli import main

CLEAN_SOURCE = "def f(x):\n    return x\n"

LEAKY_SOURCE = (
    "from functools import lru_cache\n"
    "\n"
    "class Foo:\n"
    "    @lru_cache(maxsize=None)\n"
    "    def method(self, x):\n"
    "        return x\n"
)


@pytest.fixture
def write_py(tmp_path: Path):
    def _write(name: str, source: str) -> Path:
        target = tmp_path / name
        target.write_text(source, encoding="utf-8")
        return target

    return _write


def test_clean_file_returns_zero_with_no_output(write_py, capsys):
    target = write_py("clean.py", CLEAN_SOURCE)

    exit_code = main([str(target)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""


def test_leaky_file_returns_one_and_prints_codes(write_py, capsys):
    target = write_py("leaky.py", LEAKY_SOURCE)

    exit_code = main([str(target)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "LRU001" in captured.out
    assert "LRU002" in captured.out


def test_directory_input_walks_recursively(write_py, tmp_path: Path, capsys):
    write_py("a.py", CLEAN_SOURCE)
    write_py("b.py", LEAKY_SOURCE)
    nested = tmp_path / "pkg"
    nested.mkdir()
    (nested / "c.py").write_text(LEAKY_SOURCE, encoding="utf-8")

    exit_code = main([str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out.count("LRU001") == 2
    assert captured.out.count("LRU002") == 2


def test_missing_path_returns_two_and_logs_to_stderr(tmp_path: Path, capsys):
    nonexistent = tmp_path / "does-not-exist"

    exit_code = main([str(nonexistent)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "path does not exist" in captured.err


def test_syntax_error_returns_two_and_skips_file(write_py, capsys):
    target = write_py("broken.py", "def f(\n")

    exit_code = main([str(target)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "syntax error" in captured.err


def test_output_is_sorted_by_path_then_line(write_py, tmp_path: Path, capsys):
    write_py("z_first.py", LEAKY_SOURCE)
    write_py("a_first.py", LEAKY_SOURCE)

    main([str(tmp_path)])
    captured = capsys.readouterr()
    output_lines = captured.out.strip().splitlines()

    paths = [line.split(":")[0] for line in output_lines]
    assert paths == sorted(paths)


def test_version_flag_prints_version_and_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "lrucheck" in captured.out
