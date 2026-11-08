from pathlib import Path
from spur.parser import parse_php_file, extract_symbols


def index_project(project_path: str) -> list[dict]:
    root = Path(project_path)
    if not root.is_dir():
        raise NotADirectoryError(f"Directory not found: {project_path}")

    index = []
    for php_file in root.rglob("*.php"):
        try:
            result = parse_php_file(str(php_file))
            symbols = extract_symbols(result["tree"])

            for symbol in symbols:
                index.append(
                    {
                        **symbol,
                        "file": str(php_file.relative_to(root)),
                    }
                )

        except Exception as error:
            print(f"Warning: Could not parse {php_file}: {error}")

    return index
