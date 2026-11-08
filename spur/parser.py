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
                qualified_name = (
                    f"{current_namespace}\\{container_name}"
                    if current_namespace
                    else container_name
                )
                symbols.append(
                    {
                        "type": containers[node.type],
                        "name": container_name,
                        "qualified_name": qualified_name,
                        "line": node.start_point.row + 1,
                        "container": None,
                        "namespace": current_namespace,
                    }
                )
                current_container = container_name

        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                method_name = name_node.text.decode("utf-8")
                qualified_name = (
                    f"{current_namespace}\\{current_container}::{method_name}"
                    if current_namespace and current_container
                    else f"{current_container}::{method_name}"
                    if current_container
                    else method_name
                )
                symbols.append(
                    {
                        "type": "method",
                        "name": name_node.text.decode("utf-8"),
                        "qualified_name": qualified_name,
                        "line": node.start_point.row + 1,
                        "container": current_container,
                        "namespace": current_namespace,
                    }
                )

        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                function_name = name_node.text.decode("utf-8")
                qualified_name = (
                    f"{current_namespace}\\{function_name}"
                    if current_namespace
                    else function_name
                )

                symbols.append(
                    {
                        "type": "function",
                        "name": name_node.text.decode("utf-8"),
                        "qualified_name": qualified_name,
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


def extract_imports(tree) -> list[dict]:
    imports = []

    def walk(node):
        if node.type == "namespace_use_clause":
            imported_name = None
            alias_node = node.child_by_field_name("alias")

            for child in node.children:
                if child.type == "qualified_name":
                    imported_name = child.text.decode("utf-8")

            if imported_name is not None:
                imports.append(
                    {
                        "qualified_name": imported_name,
                        "alias": alias_node.text.decode("utf-8")
                        if alias_node is not None
                        else imported_name.split("\\")[-1],
                        "line": node.start_point.row + 1,
                    }
                )

        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return imports


def extract_dependencies(tree) -> list[dict]:
    dependencies = []

    dependency_types = {
        "require_once_expression": "require_once",
        "require_expression": "require",
        "include_once_expression": "include_once",
        "include_expression": "include",
    }

    def walk(node):
        if node.type in dependency_types:
            path_node = None

            def find_path(child):
                nonlocal path_node  # allows find_path to modify path_node cases of external vars

                if child.type == "encapsed_string":
                    path_node = child

                for nested_child in child.children:
                    find_path(nested_child)

            find_path(node)

            if path_node is not None:
                dependencies.append(
                    {
                        "type": dependency_types[node.type],
                        "path": path_node.text.decode("utf-8").strip("\"'"),
                        "line": node.start_point.row + 1,
                    }
                )

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return dependencies
