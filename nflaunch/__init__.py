"""nflaunch - Nextflow launcher for cloud backends.

A command-line tool designed to simplify the launching of Nextflow pipelines
on cloud batch services.
"""

try:
    from importlib.metadata import version
    __version__ = version("nflaunch")
except Exception:
    __version__ = "0.0.0.dev"

from nflaunch.cli.main import main

__all__ = ["main", "__version__"]
