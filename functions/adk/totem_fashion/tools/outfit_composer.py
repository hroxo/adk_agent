"""
Outfit composition utilities for the Fashion Finder.

Given a seed product (the item the user likes), this module can assemble a
coordinated outfit by selecting additional items from the catalog. The
functionality here is intentionally simple: it defines a mapping between
categories to suggest possible complements, and a very basic color
harmonisation to find matching colors. For a more sophisticated styling,
these mappings and palettes can be expanded.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .catalog_search import catalog_search


# Suggest complementary categories for a given category
_COMPLEMENT = {
    "Casaco Bomber": ["Camisola de Malha", "Calças de Ganga Skinny", "Calças de Ganga Wide Leg"],
    "Camisola de Malha": ["Calças de Ganga Skinny", "Calças Marine", "Casaco Bomber"],
    "Pijama Polar de Natal": ["Pijama Polar de Natal"],
    "Polo Jersey": ["Calças Loose Fit", "Casaco Bomber"],
    "Calças Loose Fit": ["Polo Jersey", "Casaco Bomber"],
    "Calças de Ganga Wide Leg": ["Camisola de Malha", "Casaco Bomber"],
    # Add more mappings as the dataset expands
}


def _harmonize_colors(color: Optional[str]) -> List[str]:
    """Return a list of colors that pair well with the given color.

    This simple palette is based on intuitive combinations; feel free to
    expand with more nuanced rules. If color is None or not found, return
    an empty list to allow broader matching.
    """
    if not color:
        return []
    palette = {
        "bege": ["castanho", "branco", "bege claro", "preto"],
        "cinzento escuro": ["preto", "branco", "rosa"],
        "verde": ["preto", "bege", "branco"],
        "multicor": [],  # no specific harmonies
        "branco": ["preto", "bege", "azul escuro"],
        "preto": ["branco", "bege", "azul escuro"],
        "bege claro": ["bege", "castanho", "branco"],
        "azul escuro": ["branco", "bege", "preto"],
        "rosa": ["branco", "bege", "preto"],
        # Extend with more colors from the dataset
    }
    return palette.get(color.lower(), [])


def compose_outfit_from_seed(seed: Dict[str, Any], budget: Optional[float] = None) -> Dict[str, Any]:
    """Given a seed product, assemble a list of complementary items.

    Args:
        seed: The base product dict from which to build an outfit.
        budget: Optional maximum total price for the outfit; if provided,
            items that would cause the total to exceed the budget are skipped.

    Returns:
        A dict containing the selected items, the total price, and an
        explanation string.
    """
    seed_cat = seed.get("category")
    seed_color = seed.get("color")
    seed_price = float(seed.get("price", 0.0))

    # Determine target categories. Use fallback if none defined.
    target_cats = _COMPLEMENT.get(seed_cat, [])
    if not target_cats:
        # fallback: choose up to 3 different categories other than the seed category
        # get unique categories from the catalog
        from .data_loader import ITEMS
        all_cats = sorted(set(item.get("category") for item in ITEMS))
        target_cats = [c for c in all_cats if c != seed_cat][:3]

    # Determine matching colors
    colors = _harmonize_colors(seed_color)
    if not colors:
        colors = [seed_color] if seed_color else []

    outfit: List[Dict[str, Any]] = [seed]
    total_price = seed_price

    for cat in target_cats:
        # Search for items in this category that match one of the preferred colors
        item = None
        for color in colors:
            results = catalog_search(category=cat, color=color, limit=1)
            if results:
                item = results[0]
                break
        # If no color match, pick the first item in the category
        if item is None:
            results = catalog_search(category=cat, limit=1)
            item = results[0] if results else None
        # Add to outfit if found and within budget
        if item:
            if budget is not None and total_price + float(item.get("price", 0.0)) > budget:
                continue
            outfit.append(item)
            total_price += float(item.get("price", 0.0))

    return {
        "items": outfit,
        "total_price": round(total_price, 2),
        "explanation": f"Outfit baseado em '{seed.get('name')}', com cores e categorias complementares.",
    }
