"""Tests for output."""

from build_profiler.profiler import ModuleStats
from build_profiler.output import to_json, _format_size, _get_suggestions


def test_format_size():
    """Format bytes correctly."""
    assert _format_size(500) == "500B"
    assert _format_size(1024) == "1.0KB"
    assert _format_size(1024 * 1024) == "1.0MB"


def test_to_json():
    """Convert modules to JSON."""
    modules = [ModuleStats("test.js", 1024, 10.0, [])]
    result = to_json(modules)

    assert "test.js" in result
    assert "1024" in result


def test_suggestions_moment():
    """Suggest alternatives for moment.js."""
    modules = [ModuleStats("node_modules/moment/moment.js", 300000, 0, [])]
    suggestions = _get_suggestions(modules)

    assert any("moment" in s.lower() for s in suggestions)


def test_suggestions_lodash():
    """Suggest alternatives for lodash."""
    modules = [ModuleStats("node_modules/lodash/lodash.js", 100000, 0, [])]
    suggestions = _get_suggestions(modules)

    assert any("lodash" in s.lower() for s in suggestions)
