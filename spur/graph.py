from pathlib import Path
import os


def build_graph(index: dict) -> dict: #build directed graph of dependencies 

    graph = {
        "nodes": [],
        "edges": [],
        "unresolved": [],
    }

    indexed_files = {file["path"] for file in index["files"]}

    graph["nodes"] = sorted(indexed_files)

    #must process all require statements
    for dependency in index["dependencies"]:
        source_file = Path(dependency["file"])
        dependency_path = Path(dependency["path"])

        #only relative paths for now
        if dependency_path.is_absolute():
            graph["unresolved"].append(dependency)
            print("Absolute paths not supported.")
            continue

        #resolve path relative to file w require statement
        target_file = os.path.normpath(str(source_file.parent / dependency_path))

        if target_file in indexed_files:
            graph["edges"].append(
                {
                    "source": dependency["file"],
                    "target": target_file,
                    "type": dependency["type"],
                    "line": dependency["line"],
                }
            )
        else:
            graph["unresolved"].append(
                {
                    **dependency,
                    "resolved_path": target_file,
                }
            )

    return graph
