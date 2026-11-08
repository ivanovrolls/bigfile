from pathlib import Path

from spur.parser import (
    parse_php_file,
    extract_symbols,
    extract_references,
    extract_imports,
    extract_dependencies,
)


def index_project(project_path: str) -> dict:
    root = Path(project_path)

    if not root.is_dir():
        raise NotADirectoryError(f"Directory not found: {project_path}")

    index = {
        "files": [],
        "symbols": [],
        "references": [],
        "imports": [],
        "dependencies": [],
        "errors": [],
    }

    for php_file in root.rglob("*.php"):
        relative_path = str(php_file.relative_to(root))

        try:  # separation of references and imports from symbols
            result = parse_php_file(str(php_file))
            tree = result["tree"]

            index["files"].append(
                {
                    "path": relative_path,
                    "lines": result["lines"],
                }
            )

            for symbol in extract_symbols(tree):
                index["symbols"].append(
                    {
                        **symbol,
                        "file": relative_path,
                        # All symbols will now be matched with their file so spur can
                        # make the relationship for imports and references throughout
                        # the project
                    }
                )

            for reference in extract_references(tree):
                index["references"].append(
                    {
                        **reference,
                        "file": relative_path,
                    }
                )

            for imported in extract_imports(tree):
                index["imports"].append(
                    {
                        **imported,
                        "file": relative_path,
                    }
                )

            for dependency in extract_dependencies(tree):
                index["dependencies"].append(
                    {
                        **dependency,
                        "file": relative_path,
                    }
                )

        except Exception as error:
            index["errors"].append(
                {
                    "file": relative_path,
                    "error": str(error),
                }
            )

    return index
