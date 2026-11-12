from collections import (
    deque,
)  # dequeue stands for double ended queue bro dont get confused agn
from graph.py import adjacency


def reachable_from(graph: dict, start_file: str) -> tuple[list[str], dict[str, str]]:

    if start_file not in set(graph["nodes"]):
        raise ValueError(f"{start_file} not found in project")

    adjacency_dict = adjacency(graph)

    queue = deque([start_file])
    parents = {}  # this records which file each dependency was discovered from during BFS
    found = {start_file}
    dependencies = []

    while queue:
        current_file = queue.popleft()
        for neighbour in adjacency.get(current_file, []):
            if neighbour not in found:
                found.add(neighbour)
                dependencies.append(neighbour)
                queue.append(neighbour)
                parents[neighbour] = current_file

    return dependencies, parents


def get_dependencies(
    graph: dict, start_file
) -> dict:  # responsible fro creating a directory of dependencies for the given file -> dict #uses bfs to find all dependencies
    dependencies, parents = reachable_from(graph, start_file)

    return {
        "start_file": start_file,
        "dependencies": dependencies,
        "parents": parents,
    }
