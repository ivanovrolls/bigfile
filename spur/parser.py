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


def extract_symbols(tree) -> list[dict]:
    # extract classes, methods and functs fromsyntax tree
    symbols = []

    def walk(node, current_class=None):

        if node.type == "class_declaration":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                class_name = name_node.text.decode("utf-8")

                symbols.append(
                    {
                        "type": "class",
                        "name": class_name,
                        "line": node.start_point.row + 1,
                        "class": None,
                    }
                )

                current_class = class_name

        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                symbols.append(
                    {
                        "type": "method",
                        "name": name_node.text.decode("utf-8"),
                        "line": node.start_point.row + 1,
                        "class": current_class,
                    }
                )

        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                symbols.append(
                    {
                        "type": "function",
                        "name": name_node.text.decode("utf-8"),
                        "line": node.start_point.row + 1,
                        "class": None,
                    }
                )

        for child in node.children:
            walk(child, current_class)

    walk(tree.root_node)

    return symbols
