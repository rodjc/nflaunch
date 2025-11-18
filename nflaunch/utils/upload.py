"""
Backend-agnostic helpers for staging files and directories prior to upload.
"""

from collections.abc import Iterable
from pathlib import Path


def iter_directory_files(root: Path, exclude_dirs: Iterable[str] | None = None) -> list[Path]:
    """
    Return file paths under `root`, skipping directories listed in `exclude_dirs`.

    Args:
        root: Directory whose contents should be traversed recursively.
        exclude_dirs: Directory names to ignore during traversal.

    Returns:
        List of resolved `Path` objects for files under `root`.
    """
    exclude = set(exclude_dirs or [])
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir() and any(part in exclude for part in path.parts):
            continue
        if path.is_file() and not any(part in exclude for part in path.parts):
            files.append(path)
    return files


def relative_paths(files: Iterable[Path], base: Path) -> list[Path]:
    """
    Convert files into paths relative to a common base directory.

    Args:
        files: Collection of file paths.
        base: Directory to use as the relative anchor.

    Returns:
        Paths rewritten relative to `base`.
    """
    base = base.resolve()
    return [f.resolve().relative_to(base) for f in files]
