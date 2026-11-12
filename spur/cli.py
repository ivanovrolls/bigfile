from pathlib import Path
import json
from spur.deps import get_dependencies, get_dependents
import typer
from rich.console import Console
from rich.panel import Panel
from spur.graph import build_graph
from spur.trace import trace_function
from spur.display import (
    display_deps,
    display_dependents,
    display_trace,
    display_references,
    display_root,
)
from spur.helpers import to_project_relative, find_project_root

from spur.indexer import index_project
from spur.resolver import find_references

# configuration of commands

app = typer.Typer(
    help="SPUR - PHP codebase navigation and dependency analysis",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main():
    """SPUR - Static PHP Usage Railway"""
    pass


@app.command("needs")
def deps(
    file: Path = typer.Argument(
        ...,
        help="The file that you wish to analyse for dependencies",
    ),
    project: Path | None = typer.Option(
        None, "--project", "-p", help="PHP project root (auto-detected if omitted)"
    ),
    top_down: bool = typer.Option(
        False,
        "--top-down",
        "-t",
        help="Show the start file at the top instead of the bottom",
    ),
):
    # Analyse a file's dependencies without requiring a function
    try:
        root = project or find_project_root(Path.cwd())
        index = index_project(str(root))
        graph = build_graph(index)

        start_file = to_project_relative(file, root)

        result = get_dependencies(
            graph,
            start_file,
        )

        display_deps(result, top_down=top_down)
        display_root(root)

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def why(
    file: Path = typer.Argument(
        ...,
        help="The file whose dependents you want to see",
    ),
    project: Path | None = typer.Option(
        None, "--project", "-p", help="PHP project root (auto-detected if omitted)"
    ),
    top_down: bool = typer.Option(
        False,
        "--top-down",
        "-t",
        help="Show the start file at the top instead of the bottom",
    ),
):
    """Show every file that includes this file, directly or indirectly."""

    try:
        root = project or find_project_root(Path.cwd())
        index = index_project(str(root))
        graph = build_graph(index)

        start_file = to_project_relative(file, root)

        result = get_dependents(
            graph,
            start_file,
        )

        display_dependents(result, top_down=top_down)
        display_root(root)

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def trace(
    file: Path = typer.Argument(
        help="PHP file to start tracing from",
    ),
    function: str = typer.Argument(
        help="Function name to trace",
    ),
    project: Path | None = typer.Option(
        None, "--project", "-p", help="PHP project root (auto-detected if omitted)"
    ),
    text_only: bool = typer.Option(
        False,
        "--text-only",
        "-x",
        help="Display trace as text instead of a railway",
    ),
):
    """Trace a function through its file dependencies."""

    try:
        root = project or find_project_root(Path.cwd())
        index = index_project(str(root))
        graph = build_graph(index)

        # make the starting file relative to the project root
        start_file = to_project_relative(file, root)

        result = trace_function(
            index,
            graph,
            start_file,
            function,
        )

        display_trace(result, text_only=text_only)
        display_root(root)

    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def references(
    symbol: str = typer.Argument(help="Function name to find references for"),
    project: Path | None = typer.Option(
        None, "--project", "-p", help="PHP project root (auto-detected if omitted)"
    ),
):  # find definition and references of a funct

    try:
        root = project or find_project_root(Path.cwd())
        index = index_project(str(root))
        result = find_references(index, symbol)
        display_references(result)
        display_root(root)

    except (FileNotFoundError, NotADirectoryError) as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def index(
    project: Path | None = typer.Argument(
        None,
        help="PHP project directory to index (auto-detected if omitted)",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Where to save the generated JSON index",
    ),
):
    # Index php project, save extracted info

    try:
        root = project or find_project_root(Path.cwd())
        output = output or root / ".spur" / "index.json"
        project_index = index_project(str(root))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(project_index, indent=2),
            encoding="utf-8",
        )

        console.print(
            Panel(
                "[bold cyan]Project indexing complete[/bold cyan]",
                title="SPUR",
            )
        )

        console.print(f"Files:        {len(project_index['files'])}")
        console.print(f"Symbols:      {len(project_index['symbols'])}")
        console.print(f"References:   {len(project_index['references'])}")
        console.print(f"Imports:      {len(project_index['imports'])}")
        console.print(f"Dependencies: {len(project_index['dependencies'])}")
        console.print(f"Errors:       {len(project_index['errors'])}")

        console.print(f"\n[dim]Index saved to: {output}[/dim]")

        if project_index["errors"]:
            console.print("\n[yellow]Files with parsing errors:[/yellow]")

            for error in project_index["errors"]:
                console.print(f"  {error['file']}: {error['error']}")

        display_root(root)

    except NotADirectoryError as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
