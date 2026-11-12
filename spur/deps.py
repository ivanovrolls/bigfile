from collections import (
    deque,
)  # dequeue stands for double ended queue bro dont get confused agn
from spur.graph import adjacency


def reachable_from(
    neighbours: dict, nodes: list[str], start_file: str
) -> tuple[list[str], dict[str, str]]:

    if start_file not in nodes:
        raise ValueError(f"{start_file} not found in project")

    queue = deque([start_file])
    parents = {}  # this records which file each dependency was discovered from during BFS
    found = {start_file}
    reached = []

    while queue:
        current_file = queue.popleft()
        for neighbour in neighbours.get(current_file, []):
            if neighbour not in found:
                found.add(neighbour)
                reached.append(neighbour)
                queue.append(neighbour)
                parents[neighbour] = current_file

    return reached, parents


def get_dependencies(
    graph: dict, start_file
) -> dict:  # responsible fro creating a directory of dependencies for the given file -> dict #uses bfs to find all dependencies
    dependencies, parents = reachable_from(adjacency(graph), graph["nodes"], start_file)

    return {
        "start_file": start_file,
        "dependencies": dependencies,
        "parents": parents,
    }


def get_dependents(graph: dict, start_file: str) -> dict:
    dependents, parents = reachable_from(
        adjacency(graph, reverse=True), graph["nodes"], start_file
    )

    return {
        "start_file": start_file,
        "dependents": dependents,
        "parents": parents,
    }
