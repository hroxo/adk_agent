"""
Utility functions for inferring traits from user interaction history.

This optional module analyzes the session history to extract patterns such as
the user's most liked color. These traits can be used to refine future
recommendations. You can expand this to consider other attributes (brands,
categories, price ranges, etc.).
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Any


def infer_traits_from_history(session: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the session's likes to extract preference traits.

    Currently, this function determines the most frequently liked color. In
    future iterations, you could add more logic to detect preferred
    categories, price ranges, seasons, or styles.

    Args:
        session: Session data structure containing preferences and history.

    Returns:
        A dict of inferred traits. For example: {"preferred_color": "bege"}.
    """
    likes = session.get("preferences", {}).get("likes", [])
    if not likes:
        return {}
    colors = [p.get("color") for p in likes if p.get("color")]
    if not colors:
        return {}
    most_common = Counter(colors).most_common(1)
    return {"preferred_color": most_common[0][0]} if most_common else {}
