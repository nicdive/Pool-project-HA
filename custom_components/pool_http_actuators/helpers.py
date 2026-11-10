"""Small helpers without Home Assistant imports."""

from __future__ import annotations

import re
from unicodedata import normalize


def slugify(value: str) -> str:
    """Build a stable HA object_id from an actuator label."""
    text = normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "actuator"
