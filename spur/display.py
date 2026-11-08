from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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
