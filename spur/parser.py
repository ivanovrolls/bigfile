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
    containers = {  # interface and trait support
        "class_declaration": "class",
        "interface_declaration": "interface",
        "trait_declaration": "trait",
    }

    def walk(
        node, current_container=None, current_namespace=None
    ):  # default needed for non-parent nodes
        if node.type == "namespace_definition":
            name_node = node.child_by_field_name("name")
            if name_node is not None:
                current_namespace = name_node.text.decode("utf-8")

            body_node = node.child_by_field_name("body")
            if body_node is not None:
                walk(body_node, current_container, current_namespace)
                return current_namespace

        if node.type in containers:
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                container_name = name_node.text.decode("utf-8")
                symbols.append(
                    {
                        "type": containers[node.type],
                        "name": container_name,
                        "line": node.start_point.row + 1,
                        "container": None,
                        "namespace": current_namespace,
                    }
                )
                current_container = container_name

        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                symbols.append(
                    {
                        "type": "method",
                        "name": name_node.text.decode("utf-8"),
                        "line": node.start_point.row + 1,
                        "container": current_container,
                        "namespace": current_namespace,
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
                        "container": None,
                        "namespace": current_namespace,
                    }
                )
        for child in node.children:
            current_namespace = walk(child, current_container, current_namespace)

        return current_namespace

    walk(tree.root_node)

    return symbols
