from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
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


# --- Railway renderer --------------------------------------------------------

STATION_GAP = 8   # empty cells between neighbouring labels (the turn sits in here)
LEVEL_ROWS = 2    # rows the track moves per level change
MAX_LEVEL = 2     # levels range from -MAX_LEVEL to +MAX_LEVEL

TRACK_CHARS = {"─", "│", "╮", "╯", "╭", "╰"}


def render_railway(path: list[str]) -> None:
    """Render a route as a metro-style map with rounded box-drawing turns."""

    if not path:
        return

    # Repeatable layout for this route: every station steps up or down at random.
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

        if end_y > start_y:    # going down: ─╮ then │ then ╰─
            canvas[start_y][turn_x] = "╮"
            canvas[end_y][turn_x] = "╰"
        else:                  # going up:   ─╯ then │ then ╭─
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


def display_trace(result: dict) -> None:
    """Display the dependency route for a traced function."""

    function_name = result["function"]
    routes = result["routes"]
    unreachable = result["unreachable"]

    console.print()
    console.print(
        Panel(
            f"[bold cyan]{function_name}()[/bold cyan]",
            title="SPUR - Function Trace",
            expand=False,
        )
    )

    if not routes:
        console.print(
            f"[bold red]No dependency route found for {function_name}()[/bold red]"
        )

    for route_number, route in enumerate(routes, start=1):
        path = route["path"]
        definition = route["definition"]

        if len(routes) > 1:
            console.print(f"\n[bold yellow]Route {route_number}[/bold yellow]")

        render_railway(path)

        console.print(
            f"\n  [bold green]Definition found[/bold green]: "
            f"{definition['file']}:{definition['line']}"
        )

    if unreachable:
        console.print("\n[bold yellow]Unreachable definitions:[/bold yellow]")

        for definition in unreachable:
            console.print(f"  {definition['file']}:{definition['line']}")

    console.print(f"\n[bold green]{len(routes)} route(s) found[/bold green]")
    console.print()
