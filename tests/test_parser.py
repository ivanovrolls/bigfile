from pathlib import Path

import pytest
from spur.parser import parse_php_file, extract_symbols
from spur.helpers import find_project_root


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


def test_extract_symbols(tmp_path: Path):
    php_file = tmp_path / "example.php"

    php_file.write_text(
        "<?php\n"
        "interface ExampleInterface {\n"
        "    public function authenticate(): bool;\n"
        "}\n"
        "trait ExampleTrait {\n"
        "    public function logActivity(): void {}\n"
        "}\n"
        "class ExampleClass {\n"
        "    public function index(): void {}\n"
        "}\n"
        "function validate(): bool { return true; }\n"
    )

    result = parse_php_file(str(php_file))

    print(result["tree"].root_node)
    symbols = extract_symbols(result["tree"])

    assert len(symbols) == 7

    assert symbols[0]["type"] == "interface"
    assert symbols[0]["name"] == "ExampleInterface"

    assert symbols[1]["type"] == "method"
    assert symbols[1]["container"] == "ExampleInterface"

    assert symbols[2]["type"] == "trait"
    assert symbols[2]["name"] == "ExampleTrait"

    assert symbols[3]["type"] == "method"
    assert symbols[3]["container"] == "ExampleTrait"

    assert symbols[4]["type"] == "class"
    assert symbols[4]["name"] == "ExampleClass"

    assert symbols[5]["type"] == "method"
    assert symbols[5]["container"] == "ExampleClass"

    assert symbols[6]["type"] == "function"
    assert symbols[6]["name"] == "validate"
    print(result["tree"].root_node)


def test_stray_spur_in_home_is_ignored(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".spur").mkdir()
    app = tmp_path / "repo" / "app"
    (app / "login").mkdir(parents=True)
    (tmp_path / "repo" / ".git").mkdir()
    (app / "composer.json").write_text("{}")

    assert find_project_root(app / "login") == app
