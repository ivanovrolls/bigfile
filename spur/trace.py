from collections import deque
from spur.graph import adjacency


def find_shortest_path(
    graph: dict,
    start_file: str,
    target_file: str,
) -> list[str] | None:
    # breadth first traversal - look at all of current level before going deeper into graph

    neighbours = adjacency(graph)
    # store path currently being explored
    queue = deque([[start_file]])

    visited = {start_file}  # track visited files to avoid circular dependencies

    while queue:
        path = queue.popleft()
        current_file = path[-1]

        if current_file == target_file:
            return path

        # explore files required by the current file.
        for neighbour in neighbours.get(current_file, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(path + [neighbour])

    # if u make it here, no route found
    return None


def trace_function(  # trace a function from given file to original definition
    index: dict,
    graph: dict,
    start_file: str,
    function_name: str,
) -> dict:

    # note all definitions of the request
    definitions = [
        symbol
        for symbol in index["symbols"]
        if symbol["type"] == "function" and symbol["name"] == function_name
    ]

    routes = []
    unreachable = []

    # Find a route to each definition.
    for definition in definitions:
        target_file = definition["file"]

        path = find_shortest_path(
            graph,
            start_file,
            target_file,
        )

        if path is not None:
            routes.append(
                {
                    "definition": definition,
                    "path": path,
                }
            )
        else:
            unreachable.append(definition)

    return {
        "function": function_name,
        "start_file": start_file,
        "routes": routes,
        "unreachable": unreachable,
    }
