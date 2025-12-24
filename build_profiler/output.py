"""Output formatters for build profiler."""

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .profiler import ModuleStats


def print_report(modules: List[ModuleStats], console: Console, top: int = 20):
    """Print build profile report."""
    if not modules:
        console.print("[yellow]No modules found.[/yellow]")
        return

    # Sort by size (proxy for build time)
    modules = sorted(modules, key=lambda m: m.size, reverse=True)[:top]

    total_size = sum(m.size for m in modules)

    console.print()
    console.print(f"[bold]Build Profile[/bold]")
    console.print(f"[dim]Total size: {_format_size(total_size)}[/dim]")
    console.print()

    # Table
    table = Table(title="Slowest Modules")

    table.add_column("#", style="dim")
    table.add_column("Module", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("% of Total", justify="right")

    for i, m in enumerate(modules, 1):
        pct = (m.size / total_size * 100) if total_size else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

        table.add_row(
            str(i),
            _truncate(m.name, 40),
            _format_size(m.size),
            f"[dim]{bar}[/dim] {pct:.1f}%",
        )

    console.print(table)
    console.print()

    # Suggestions
    suggestions = _get_suggestions(modules)
    if suggestions:
        console.print(Panel('\n'.join(suggestions), title="Suggestions"))


def _format_size(size: int) -> str:
    """Format bytes to human readable."""
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}MB"
    elif size >= 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size}B"


def _truncate(s: str, max_len: int) -> str:
    """Truncate string with ellipsis."""
    if len(s) <= max_len:
        return s
    return s[:max_len - 3] + "..."


def _get_suggestions(modules: List[ModuleStats]) -> List[str]:
    """Generate optimization suggestions."""
    suggestions = []

    for m in modules[:5]:
        name = m.name.lower()

        if 'moment' in name:
            suggestions.append("⚠️ moment.js: Consider date-fns or dayjs (smaller)")
        elif 'lodash' in name and 'lodash-es' not in name:
            suggestions.append("⚠️ lodash: Use lodash-es or import specific functions")
        elif 'node_modules' in name and m.size > 100 * 1024:
            suggestions.append(f"⚠️ {m.name}: Consider code-splitting for large deps")

    return suggestions


def to_json(modules: List[ModuleStats]) -> str:
    """Convert to JSON."""
    import json
    return json.dumps([{
        'name': m.name,
        'size': m.size,
        'build_time': m.build_time,
    } for m in modules], indent=2)
