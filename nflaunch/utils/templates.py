"""
Helpers for rendering template files used by backend executor configurations.
"""

from collections.abc import Mapping
from pathlib import Path
from string import Template


def render_template(template_path: Path, substitutions: Mapping[str, str]) -> str:
    """
    Read a template file and return the substituted string.

    Args:
        template_path: Path to the template file.
        substitutions: Mapping of template variables to rendered values.

    Returns:
        Rendered string with substitutions applied.
    """
    content = template_path.read_text()
    return Template(content).substitute(substitutions)
