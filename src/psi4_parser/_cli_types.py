"""Share filesystem and timeout conversion rules across the Click commands."""

from pathlib import Path

import click

# PyCharm 2026.2 checks ParamType.__call__ instead of these class constructors.
# noinspection PyArgumentList
INPUT_FILE = click.Path(exists=True, dir_okay=False, allow_dash=True, path_type=Path)
"""Existing input file, with a dash accepted for standard input."""

# noinspection PyArgumentList
DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path)
"""Existing directory supplied to a maintenance command."""

# noinspection PyArgumentList
EXECUTABLE = click.Path(exists=True, dir_okay=False, executable=True, path_type=Path)
"""Existing executable file, retaining a launcher's symlink basename."""

# noinspection PyArgumentList
OUTPUT_FILE = click.Path(dir_okay=False, path_type=Path)
"""Output file that need not exist before command execution."""

# noinspection PyArgumentList
OUTPUT_STREAM = click.Path(dir_okay=False, allow_dash=True, path_type=Path)
"""Output file, with a dash accepted for standard output."""

# noinspection PyTypeChecker
SOURCE_FORMAT = click.Choice(("psithon", "json"))
"""Supported source and high-level AST serialization formats."""

# noinspection PyArgumentList
TIMEOUT = click.FloatRange(min=0, min_open=True)
"""Strictly positive subprocess timeout in seconds."""
