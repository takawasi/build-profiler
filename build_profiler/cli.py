"""CLI interface for build-profiler."""

import sys
import click
from pathlib import Path
from rich.console import Console

from .profiler import profile_next, profile_vite
from .output import print_report, to_json

console = Console()


@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--next', 'is_next', is_flag=True, help='Profile Next.js project')
@click.option('--vite', 'is_vite', is_flag=True, help='Profile Vite project')
@click.option('--top', '-n', default=20, type=int, help='Show top N modules')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json']),
              default='table',
              help='Output format')
@click.option('--max-size', type=int, help='Fail if any module exceeds size in KB')
@click.version_option()
def main(path: str, is_next: bool, is_vite: bool, top: int, output_format: str, max_size: int):
    """Profile Next.js/Vite build times per module.

    Examples:

        build-profiler --next ./app
        build-profiler --vite ./app
        build-profiler --next ./app --top 10
    """
    project_path = Path(path).resolve()

    # Auto-detect if not specified
    if not is_next and not is_vite:
        if (project_path / 'next.config.js').exists() or (project_path / 'next.config.mjs').exists():
            is_next = True
        elif (project_path / 'vite.config.js').exists() or (project_path / 'vite.config.ts').exists():
            is_vite = True
        else:
            console.print("[red]Error:[/red] Could not detect project type. Use --next or --vite.")
            sys.exit(1)

    console.print(f"[bold blue]Profiling:[/] {project_path}", file=sys.stderr)
    console.print(f"[dim]Type: {'Next.js' if is_next else 'Vite'}[/dim]", file=sys.stderr)

    # Profile
    if is_next:
        modules = profile_next(project_path)
    else:
        modules = profile_vite(project_path)

    if not modules:
        console.print("[yellow]No build output found. Run build first.[/yellow]")
        console.print("  Next.js: npx next build")
        console.print("  Vite: npx vite build")
        sys.exit(1)

    # Output
    if output_format == 'json':
        click.echo(to_json(modules))
    else:
        print_report(modules, console, top)

    # Size check
    if max_size:
        max_bytes = max_size * 1024
        for m in modules:
            if m.size > max_bytes:
                console.print(f"[red]Error:[/red] {m.name} exceeds {max_size}KB ({m.size // 1024}KB)")
                sys.exit(1)


if __name__ == '__main__':
    main()
