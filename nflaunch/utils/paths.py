"""
Utilities for resolving and normalizing filesystem paths used across backends.
"""

import os
from pathlib import Path


def resolve_path(value: str) -> Path:
    """
    Expand environment variables and user home references, returning an absolute path.

    Args:
        value: Input path that may contain environment variables or `~`.

    Returns:
        Absolute `Path` instance pointing to the resolved location.
    """
    expanded = os.path.expandvars(os.path.expanduser(value))
    return Path(expanded).resolve()


def ensure_directory(path: Path) -> Path:
    """
    Create the directory (and parents) if it does not already exist.

    Args:
        path: Directory path to create.

    Returns:
        Resolved absolute `Path` for the directory.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()
