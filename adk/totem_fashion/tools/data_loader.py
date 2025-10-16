"""
Utilities for loading clothing data into memory.

This module reads the JSON file (db_preco.json) containing the list of available
products and exposes it as a module-level list `ITEMS`.

By loading the data at import time, we avoid repeatedly reading the file on
every search. You can override the default file location using the `DATA_FILE`
environment variable.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

# Default path to the data file relative to this module. Allows override via env.
DATA_FILE = os.getenv(
    "DATA_FILE",
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "db_preco.json",
    ),
)


def load_items() -> List[Dict[str, Any]]:
    """Load and return the list of items from the JSON file.

    The file must be encoded in UTF-8 and contain a JSON array of objects.
    Raises FileNotFoundError if the file does not exist.
    """
    with open(os.path.abspath(DATA_FILE), "r", encoding="utf-8") as fh:
        return json.load(fh)


try:
    ITEMS: List[Dict[str, Any]] = load_items()
except FileNotFoundError:
    # In development environments where the file isn't present, fallback to empty
    ITEMS = []
