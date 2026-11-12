from pathlib import Path
import os


def adjacency(graph: dict, reverse: bool = False) -> dict[str, list[str]]:
    adjacency_dict = {}
    for edge in graph["edges"]:
        source = edge["source"]
        target = edge["target"]

        if reverse:
            adjacency_dict.setdefault(target, []).append(source)
        else:
            adjacency_dict.setdefault(source, []).append(target)

    return adjacency_dict


def build_graph(index: dict) -> dict:  # build directed graph of dependencies

    graph = {
        "nodes": [],
        "edges": [],
        "unresolved": [],
    }

    indexed_files = {file["path"] for file in index["files"]}
    # indexed_files = set() wrote this out in long form cause short form is cool n all but it lowk confuses me
    #
    # for file in index["files"]:
    #     indexed_files.add(file["path"])
    graph["nodes"] = sorted(indexed_files)

    # must process all require statements
    for dependency in index["dependencies"]:
        source_file = Path(dependency["file"])
        dependency_path = Path(dependency["path"])

        # only relative paths for now
        if dependency_path.is_absolute():
            graph["unresolved"].append(dependency)
            # print("Absolute paths not supported.")
            continue

        # resolve path relative to file w require statement
        target_file = os.path.normpath(str(source_file.parent / dependency_path))

        if (
            target_file in indexed_files
        ):  # sets are easier for checking membership here than lists
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
