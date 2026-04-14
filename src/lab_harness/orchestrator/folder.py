"""Data folder organization with OS-level file explorer integration."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def prepare_data_folder(root: Path, folder_name: str) -> Path:
    """Create and return the data folder for this experiment."""
    folder = root / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def open_folder(path: Path) -> bool:
    """Open folder in the OS file explorer. Returns True if successful."""
    try:
        path = Path(path).resolve()
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except Exception as e:
        logger.warning("Could not open folder %s: %s", path, e)
        return False
