from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.segment import Segment, Segments
from pathlib import Path
import random

console = Console()


def display_index(symbols: list[dict]) -> None:
    table = Table(
        title="SPUR - Symbol Index",
        show_lines=False,
        header_style="bold cyan",
    )

    table.add_column("Type", style="green")
    table.add_column("Name", style="bold white")
    table.add_column("Qualified Name", style="magenta")
    table.add_column("Container", style="yellow")
    table.add_column("File", style="blue")
    table.add_column("Line", justify="right", style="dim")

    for symbol in symbols:
        table.add_row(
            symbol["type"],
            symbol["name"],
            symbol.get("qualified_name") or "-",
            symbol.get("container") or "-",
            symbol["file"],
            str(symbol["line"]),
        )
    console.print(table)
    console.print(
        Panel(
            f"Indexed [bold cyan]{len(symbols)}[/bold cyan] symbols",
            title="SPUR",
            border_style="cyan",
        )
    )


# --- Project root -------------------------------------------------------------


def display_root(root: Path) -> None:
    """Print the project root the command ran against, so a wrong root is obvious."""

    root = root.resolve()
    home = Path.home()

    if root == home:
        shown = "~"
    elif root.is_relative_to(home):
        shown = "~/" + root.relative_to(home).as_posix()
    else:
        shown = root.as_posix()

    console.print(Text(f"root: {shown}", style="dim"))


# --- References ----------------------------------------------------------------

REFERENCE_STATUS_STYLES = {
    "resolved": "green",
    "ambiguous": "yellow",
}


def display_references(result: dict) -> None:
    """Render where a symbol is defined and every place that references it."""

    definitions = result["definitions"]
    references = result["references"]

    console.print(
        Panel(
            Text(f"References: {result['name']}", style="bold cyan"),
            title="SPUR",
        )
    )

    console.print()
    console.print(Text("DEFINITIONS", style="bold"))

    if definitions:
        for definition in definitions:
            console.print(
                Text(f"  {definition['file']}:{definition['line']}", style="green")
            )
    else:
        console.print(Text("  No definition found", style="yellow"))

    console.print()
    console.print(Text("REFERENCED BY", style="bold"))

    if references:
        for reference in references:
            status = reference["status"]
            style = REFERENCE_STATUS_STYLES.get(status, "red")
            console.print(
                Text.assemble(
                    f"  {reference['file']}:{reference['line']} ",
                    (f"({status})", style),
                )
            )
    else:
        console.print("  No references found")

    resolved = sum(1 for reference in references if reference["status"] == "resolved")
    console.print()
    console.print(
        Text(
            f"{len(references)} reference(s) found, {resolved} resolved.",
            style="dim",
        )
    )


# --- Dependency tree ---------------------------------------------------------

# Characters rich.Tree uses for its guide lines. When the tree is flipped,
# only the "last child" corner needs to change: ┣ and ┃ look the same upside down.
TREE_GUIDE_CHARS = set("┣┗┃━ ")
FLIP_GUIDES = str.maketrans({"┗": "┏"})


def _tree_label(marker: str, marker_style: str, name: str, name_style: str) -> Text:
    # Text instead of markup string: no escaping needed, and no_wrap keeps every
    # node on exactly one line (a wrapped line would break the flipped view).
    return Text.assemble(
        (marker, marker_style),
        " ",
        (name, name_style),
        no_wrap=True,
        overflow="ellipsis",
    )


def _build_tree(start_file: str, dependencies: list[str], parents: dict) -> Tree:
    root = Tree(
        _tree_label("●", "bold yellow", start_file, "bold white"),
        guide_style="bold green",
    )
    nodes = {start_file: root}

    # BFS order guarantees a file's parent was added before the file itself,
    # so nodes[parent] always exists by the time we need it.
    for dependency in dependencies:
        parent = parents.get(dependency, start_file)
        nodes[dependency] = nodes[parent].add(
            _tree_label("○", "yellow", dependency, "cyan")
        )

    return root


def _print_flipped(tree: Tree) -> None:
    """Print a tree upside down: root on the last line, branches growing upward."""

    options = console.options.update(no_wrap=True, overflow="ellipsis")
    lines = console.render_lines(tree, options, pad=False)

    output = []
    for line in reversed(lines):
        for segment in line:
            # Only touch guide segments, never file names.
            if set(segment.text) <= TREE_GUIDE_CHARS:
                segment = Segment(
                    segment.text.translate(FLIP_GUIDES), segment.style, segment.control
                )
            output.append(segment)
        output.append(Segment.line())

    console.print(Segments(output), end="")


def display_deps(result: dict, top_down: bool = False) -> None:
    """Render a file's dependencies as a tree, nesting each file under the one that pulled it in.

    By default the tree is flipped so the start file and its direct dependencies
    end up at the bottom of the terminal, next to the prompt. top_down=True gives
    the conventional root-first layout (nicer when piping into less or a file).
    """

    start_file = result["start_file"]
    dependencies = result["dependencies"]
    # parents[file] = the file that first discovered it during BFS.
    # Missing (older get_dependencies output) -> everything hangs off the root.
    parents = result.get("parents", {})

    header = Panel(
        Text.assemble(("Dependencies: ", "bold cyan"), (start_file, "bold cyan")),
        title="SPUR",
    )
    count = Text(f"{len(dependencies)} file(s) reachable.", style="dim")

    if not dependencies:
        message = Text("No dependencies found.", style="yellow")
        if top_down:
            console.print(header)
            console.print(message)
        else:
            console.print(message)
            console.print(header)
        return

    tree = _build_tree(start_file, dependencies, parents)

    if top_down:
        console.print(header)
        console.print(tree)
        console.print()
        console.print(count)
    else:
        # Everything that summarises the result goes at the bottom, where the
        # user's eyes are when the command finishes.
        _print_flipped(tree)
        console.print()
        console.print(count)
        console.print(header)


# --- Railway renderer --------------------------------------------------------

STATION_GAP = 8  # empty cells between neighbouring labels (the turn sits in here)
LEVEL_ROWS = 2  # rows the track moves per level change
MAX_LEVEL = 2  # levels range from -MAX_LEVEL to +MAX_LEVEL

TRACK_CHARS = {"─", "│", "╮", "╯", "╭", "╰"}


def render_railway(path: list[str]) -> None:
    """Render a route as a metro-style map with rounded box-drawing turns."""

    if not path:
        return

    # repeatable layout for each route per session
    seed = sum(ord(char) for file_path in path for char in file_path)
    rng = random.Random(seed)

    levels = [0]
    for _ in range(1, len(path)):
        step = rng.choice([-1, 1])
        if abs(levels[-1] + step) > MAX_LEVEL:
            step = -step  # bounce off the top/bottom limit instead of going flat
        levels.append(levels[-1] + step)

    # Row 0 is reserved for the label of the highest station.
    top = min(levels)
    rows = [1 + (level - top) * LEVEL_ROWS for level in levels]

    # Each label is centred on its station, so it spans
    # [column - len // 2, column - len // 2 + len). Stations are spaced so that
    # neighbouring labels are always exactly STATION_GAP cells apart: long names
    # push their neighbours further away, short names pull them closer.
    def label_start(column: int, name: str) -> int:
        return column - len(name) // 2

    def label_end(column: int, name: str) -> int:
        return label_start(column, name) + len(name)

    columns = [len(path[0]) // 2]
    for previous, name in zip(path, path[1:]):
        columns.append(label_end(columns[-1], previous) + STATION_GAP + len(name) // 2)

    width = label_end(columns[-1], path[-1]) + 1
    height = max(rows) + 1
    canvas = [[" "] * width for _ in range(height)]

    # Track: flat run, rounded turn, vertical, rounded turn, flat into the station.
    # The turn sits in the middle of the gap between the two labels, so the
    # vertical part never runs through a label.
    for i in range(len(path) - 1):
        start_x, end_x = columns[i], columns[i + 1]
        start_y, end_y = rows[i], rows[i + 1]
        turn_x = (label_end(start_x, path[i]) + label_start(end_x, path[i + 1])) // 2

        for col in range(start_x, turn_x):
            canvas[start_y][col] = "─"
        for col in range(turn_x + 1, end_x):
            canvas[end_y][col] = "─"

        if end_y > start_y:  # going down: ─╮ then │ then ╰─
            canvas[start_y][turn_x] = "╮"
            canvas[end_y][turn_x] = "╰"
        else:  # going up:   ─╯ then │ then ╭─
            canvas[start_y][turn_x] = "╯"
            canvas[end_y][turn_x] = "╭"

        for row in range(min(start_y, end_y) + 1, max(start_y, end_y)):
            canvas[row][turn_x] = "│"

    # Station markers on the track, labels centred directly above them.
    label_cells = set()
    for i, (file_path, col, row) in enumerate(zip(path, columns, rows)):
        if i == 0:
            canvas[row][col] = "●"
        elif i == len(path) - 1:
            canvas[row][col] = "◎"
        else:
            canvas[row][col] = "○"

        for offset, char in enumerate(file_path):
            x = label_start(col, file_path) + offset
            canvas[row - 1][x] = char
            label_cells.add((row - 1, x))

    station_cells = set(zip(rows, columns))

    for y, canvas_row in enumerate(canvas):
        line = Text()
        for x, char in enumerate(canvas_row):
            if (y, x) in station_cells:
                line.append(char, style="bold yellow")
            elif (y, x) in label_cells:
                line.append(char, style="bold white")
            elif char in TRACK_CHARS:
                line.append(char, style="bold green")
            else:
                line.append(char)
        # Crop rather than wrap: a wrapped row would split the map apart.
        console.print(line, no_wrap=True, overflow="crop")


def display_trace(result: dict, text_only: bool = False):
    function_name = result["function"]
    routes = result["routes"]
    unreachable = result["unreachable"]

    console.print(
        Panel(
            f"[bold cyan]Tracing: {function_name}[/bold cyan]",
            title="SPUR",
        )
    )

    if not routes:
        console.print("[yellow]No dependency route found.[/yellow]")

    for i, route in enumerate(routes, start=1):
        path = route["path"]
        definition = route["definition"]

        if len(routes) > 1:
            console.print(f"\n[bold]Route {i}[/bold]")

        if text_only:
            for j, file_path in enumerate(path):
                console.print(f"[cyan]{file_path}[/cyan]")

                if j < len(path) - 1:
                    console.print("    [green]↓[/green]")
        else:
            render_railway(path)

        console.print(
            f"\n[green]Definition:[/green] {definition['file']}:{definition['line']}"
        )

    if unreachable:
        console.print("\n[yellow]Unreachable definitions:[/yellow]")
        for definition in unreachable:
            console.print(f"  {definition['file']}:{definition['line']}")

    console.print(f"\n[dim]{len(routes)} route(s) found.[/dim]")
