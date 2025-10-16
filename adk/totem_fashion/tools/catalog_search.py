"""
Search utilities for the Fashion Finder.

This module provides the `catalog_search` function which filters the in-memory
list of items by various attributes (query, category, color, gender, price).

By performing the search in memory, the system avoids network calls and works
without a backend server. For larger datasets or production use, you may want
to back this with a database or search engine.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .data_loader import ITEMS


def catalog_search(
    query: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    gender: Optional[str] = None,
    price_max: Optional[float] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Filter the ITEMS list based on the provided parameters.

    Args:
        query: Text to search for in the name, category, or brand.
        category: Exact category name to match (case-insensitive).
        color: A color or substring to look for in the color field.
        gender: Exact gender to match ("Homem" or "Mulher").
        price_max: If provided, only include items whose price is <= this value.
        limit: Maximum number of results to return.

    Returns:
        A list of item dicts matching the filters, truncated to the given limit.
    """
    # Start with the full dataset
    results: List[Dict[str, Any]] = ITEMS.copy()

    if query:
        q = query.lower()
        results = [
            item
            for item in results
            if q in item.get("name", "").lower()
            or q in item.get("category", "").lower()
            or q in item.get("brand", "").lower()
        ]

    if category:
        results = [
            item for item in results if item.get("category", "").lower() == category.lower()
        ]

    if color:
        c = color.lower()
        results = [
            item
            for item in results
            if c in item.get("color", "").lower()
        ]

    if gender:
        results = [
            item for item in results if item.get("gender", "").lower() == gender.lower()
        ]

    if price_max is not None:
        results = [item for item in results if item.get("price") is not None and item["price"] <= price_max]

    return results[:limit]
