"""Replace file contents atomically with explicit permission and durability choices."""

import os
import tempfile
from pathlib import Path


def atomic_replace(
    path: Path, content: bytes, *, mode: int | None = None, sync: bool = False
) -> None:
    """Replace bytes and remove the temporary file when an operation fails.

    Args:
        path: Destination in an existing directory; symlinks are handled by callers.
        content: Complete replacement bytes.
        mode: Permissions to apply, or None to retain temporary-file permissions.
        sync: Flush and synchronize the file contents before replacement.
    """
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=".psi4-parser-", delete=False
        ) as stream:
            replacement = Path(stream.name)
            temporary = replacement
            stream.write(content)
            if sync:
                stream.flush()
                os.fsync(stream.fileno())
        if mode is not None:
            replacement.chmod(mode)
        replacement.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
