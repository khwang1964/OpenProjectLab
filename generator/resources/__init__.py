"""Package-owned runtime resources for OpenProjectLab."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def package_template_root() -> Path:
    """Return the installed package-owned template root.

    OpenProjectLab wheels are installed as normal filesystem packages by pip.
    The returned path is therefore suitable for the existing Path-based
    TemplateRenderer boundary.
    """
    root = Path(str(files("generator.resources").joinpath("templates")))
    if not root.is_dir():
        raise FileNotFoundError(f"OpenProjectLab packaged template resources are missing: {root}")
    return root


__all__ = ["package_template_root"]
