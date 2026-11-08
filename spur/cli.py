from pathlib import Path
import json
import typer
from rich.console import Console
from rich.panel import Panel

from spur.indexer import index_project
from spur.resolver import find_references

app = typer.Typer(
    help="SPUR - PHP codebase navigation and dependency analysis",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main():
    """SPUR - PHP codebase navigation and dependency analysis."""
    pass


@app.command()
def references(
    symbol: str = typer.Argument(help="Function name to find references for"),
    project: Path = typer.Option(
        Path("."),
        "--project",
        "-p",
        help="PHP project directory to analyse",
    ),
):
    """Find the definition and references of a PHP function."""

    try:
        index = index_project(str(project))
        result = find_references(index, symbol)

        console.print(
            Panel(
                f"[bold cyan]References: {result['name']}[/bold cyan]",
                title="SPUR",
            )
        )

        console.print("\n[bold]DEFINITIONS[/bold]")

        if result["definitions"]:
            for definition in result["definitions"]:
                console.print(
                    f"  [green]{definition['file']}:{definition['line']}[/green]"
                )
        else:
            console.print("  [yellow]No definition found[/yellow]")

        console.print("\n[bold]REFERENCED BY[/bold]")

        if result["references"]:
            for reference in result["references"]:
                status = reference["status"]

                if status == "resolved":
                    style = "green"
                elif status == "ambiguous":
                    style = "yellow"
                else:
                    style = "red"
                console.print(
                    f"  {reference['file']}:{reference['line']} "
                    f"[{style}][({status})][/{style}]"
                )
        else:
            console.print("  No resolved references found")

        console.print(
            f"\n[dim]{len(result['references'])} resolved reference(s) found.[/dim]"
        )

    except (FileNotFoundError, NotADirectoryError) as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


@app.command()
def index(
    project: Path = typer.Argument(
        Path("."),
        help="PHP project directory to index",
    ),
    output: Path = typer.Option(
        Path(".spur/index.json"),
        "--output",
        "-o",
        help="Where to save the generated JSON index",
    ),
):
    # Index a php project and save its extracted info

    try:
        project_index = index_project(str(project))
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

    except NotADirectoryError as error:
        console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
