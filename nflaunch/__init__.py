"""nflaunch - Nextflow launcher for cloud backends.

A command-line tool designed to simplify the launching of Nextflow pipelines
on cloud batch services.
"""

__version__ = "0.1.0"

from nflaunch.cli.main import main

__all__ = ["main", "__version__"]
