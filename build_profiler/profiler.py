"""Build profiler - Analyze webpack stats."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ModuleStats:
    """Stats for a single module."""
    name: str
    size: int  # bytes
    build_time: float  # ms (estimated)
    chunks: List[str]


def profile_next(path: Path, analyze: bool = True) -> List[ModuleStats]:
    """Profile Next.js build.

    Runs 'next build' with ANALYZE=true if available,
    or parses .next/build-manifest.json for basic info.
    """
    modules = []

    # Check for .next directory
    next_dir = path / '.next'
    if not next_dir.exists():
        # Run build
        env = {'ANALYZE': 'true'} if analyze else {}
        subprocess.run(
            ['npx', 'next', 'build'],
            cwd=path,
            env=env,
            capture_output=True,
        )

    # Parse build manifest
    manifest_path = next_dir / 'build-manifest.json'
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text())
        modules.extend(_parse_next_manifest(data, next_dir))

    # Parse webpack stats if available
    stats_path = path / '.next' / 'server' / 'webpack-stats.json'
    if stats_path.exists():
        data = json.loads(stats_path.read_text())
        modules.extend(_parse_webpack_stats(data))

    return _deduplicate(modules)


def profile_vite(path: Path) -> List[ModuleStats]:
    """Profile Vite build.

    Parses rollup bundle output for module sizes.
    """
    modules = []

    # Check for dist directory
    dist_dir = path / 'dist'

    if not dist_dir.exists():
        # Run build
        subprocess.run(
            ['npx', 'vite', 'build'],
            cwd=path,
            capture_output=True,
        )

    # Parse meta files
    meta_files = list(dist_dir.rglob('*.meta.json'))
    for meta in meta_files:
        try:
            data = json.loads(meta.read_text())
            modules.extend(_parse_vite_meta(data))
        except Exception:
            pass

    # Fallback: analyze output files
    if not modules:
        for js_file in dist_dir.rglob('*.js'):
            size = js_file.stat().st_size
            modules.append(ModuleStats(
                name=str(js_file.relative_to(dist_dir)),
                size=size,
                build_time=size / 1000,  # Rough estimate: 1KB = 1ms
                chunks=[],
            ))

    return modules


def _parse_next_manifest(data: Dict, next_dir: Path) -> List[ModuleStats]:
    """Parse Next.js build-manifest.json."""
    modules = []

    pages = data.get('pages', {})
    for page, files in pages.items():
        total_size = 0
        for file in files:
            file_path = next_dir / 'static' / file
            if file_path.exists():
                total_size += file_path.stat().st_size

        modules.append(ModuleStats(
            name=page,
            size=total_size,
            build_time=total_size / 1000,  # Estimate
            chunks=files,
        ))

    return modules


def _parse_webpack_stats(data: Dict) -> List[ModuleStats]:
    """Parse webpack stats.json."""
    modules = []

    for module in data.get('modules', []):
        modules.append(ModuleStats(
            name=module.get('name', 'unknown'),
            size=module.get('size', 0),
            build_time=module.get('profile', {}).get('total', 0),
            chunks=module.get('chunks', []),
        ))

    return modules


def _parse_vite_meta(data: Dict) -> List[ModuleStats]:
    """Parse Vite/Rollup meta.json."""
    modules = []

    for output, info in data.get('outputs', {}).items():
        modules.append(ModuleStats(
            name=output,
            size=info.get('bytes', 0),
            build_time=0,
            chunks=[],
        ))

    return modules


def _deduplicate(modules: List[ModuleStats]) -> List[ModuleStats]:
    """Remove duplicates by name."""
    seen = set()
    unique = []
    for m in modules:
        if m.name not in seen:
            seen.add(m.name)
            unique.append(m)
    return unique
