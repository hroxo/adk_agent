"""
High-level agent class for the Fashion Finder.

This agent exposes methods for the two main interactions with the mirror:
1. Discovering items (initial card swipes)
2. Creating an outfit from a selected seed item

It integrates the SessionManager and the various tools to record preferences
and compose outfits.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .session import SessionManager
from ..tools.catalog_search import catalog_search
from ..tools.preference_store import PreferenceStoreTool
from ..tools.outfit_composer import compose_outfit_from_seed
from ..tools.history_recall import infer_traits_from_history


class FashionStylistAgent:
    """Central coordinator for styling recommendations."""

    def __init__(self, session_manager: Optional[SessionManager] = None) -> None:
        self.sm = session_manager or SessionManager()
        self.prefs = PreferenceStoreTool(self.sm)

    # --- Discovery mode (Tinder-like) ---
    def discover(self, session_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return a batch of items for the user to swipe through."""
        return catalog_search(category=category, limit=30)

    def swipe_like(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a 'like' event and return fresh suggestions."""
        self.prefs.like(session_id, product)
        return self._recommend_from_profile(session_id)

    def swipe_dislike(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a 'dislike' event and return fresh suggestions."""
        self.prefs.dislike(session_id, product)
        return self._recommend_from_profile(session_id)

    # --- Outfit mode ---
    def create_outfit_from_seed(self, session_id: str, seed_id: str, budget: Optional[float] = None) -> Dict[str, Any]:
        """Compose an outfit starting from a seed item id."""
        seed = self._get_product_by_id(seed_id)
        return compose_outfit_from_seed(seed, budget)

    # --- Internal helpers ---
    def _recommend_from_profile(self, session_id: str) -> Dict[str, Any]:
        """Generate recommendations based on the session's inferred traits."""
        session = self.sm.get_session(session_id)
        traits = infer_traits_from_history(session)
        color = traits.get("preferred_color")
        # If a preferred color exists, filter by that; otherwise, general list
        suggestions = catalog_search(color=color, limit=12) if color else catalog_search(limit=12)
        hint = (
            f"Baseado na tua preferência por {color}"
            if color
            else "Baseado nas tuas interacções recentes"
        )
        return {
            "suggestions": suggestions,
            "hint": hint,
        }

    def _get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Look up a single product by id in the data set."""
        from ..tools.data_loader import ITEMS
        for item in ITEMS:
            if item.get("id") == product_id:
                return item
        raise ValueError(f"Produto com id '{product_id}' não encontrado")
