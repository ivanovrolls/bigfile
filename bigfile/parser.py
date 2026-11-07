from pathlib import Path

import tree_sitter_php as tsp
from tree_sitter import Language, Parser

PHP_LANGUAGE = Language(tsp.language_php())
PHP_PARSER = Parser(PHP_LANGUAGE)


def parse_php_file(file_path: str) -> dict:  # parse a php file, return struct info
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    source_code = path.read_bytes()
    tree = PHP_PARSER.parse(source_code)

    return {
        "file": path.name,
        "lines": len(source_code.splitlines()),
        "tree": tree,  # syntax tree - structure representation of source code
    }
