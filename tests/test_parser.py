from pathlib import Path

import pytest
from bigfile.parser import parse_php_file


def test_parse_php_file(tmp_path: Path):
    php_file = tmp_path / "example.php"

    php_file.write_text("<?php\nclass Example {}\n")

    result = parse_php_file(str(php_file))

    assert result["file"] == "example.php"
    assert result["lines"] == 2
    assert result["tree"] is not None


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_php_file("missing.php")
