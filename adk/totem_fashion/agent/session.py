"""
Session management for the Totem Fashion Finder agent.

This module defines a simple in-memory session store and a session manager
that records user likes, dislikes, traits and history.
You can swap the underlying store with a different backend (e.g. Firestore)
by implementing the BaseSessionStore interface.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class BaseSessionStore:
    """Abstract interface for a session store.

    Subclasses should implement get, put and update to persist session data.
    """

    def get(self, session_id: str) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    def put(self, session_id: str, data: Dict[str, Any]) -> None:  # pragma: no cover
        raise NotImplementedError

    def update(self, session_id: str, patch: Dict[str, Any]) -> None:  # pragma: no cover
        raise NotImplementedError


class InMemoryStore(BaseSessionStore):
    """A simple in-memory session storage for demo and testing purposes."""

    def __init__(self) -> None:
        # Dictionary keyed by session_id storing session data dicts
        self._mem: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        """Return the session dict for a given session_id, creating it if absent."""
        return self._mem.setdefault(
            session_id,
            {
                "created_at": time.time(),
                "preferences": {"likes": [], "dislikes": []},
                "traits": {},
                "history": [],
            },
        )

    def put(self, session_id: str, data: Dict[str, Any]) -> None:
        """Overwrite the session data for a given id."""
        self._mem[session_id] = data

    def update(self, session_id: str, patch: Dict[str, Any]) -> None:
        """Update nested keys in the session data.

        Performs a shallow merge of dicts for nested structures.
        """
        base = self.get(session_id)
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                # update nested dicts
                base[key].update(value)
            else:
                base[key] = value


def _slim(product: Dict[str, Any]) -> Dict[str, Any]:
    """Return a slim representation of a product for storage.

    Only keep a subset of fields to avoid storing large objects in session.
    """
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "category": product.get("category"),
        "color": product.get("color"),
        "price": product.get("price"),
    }


class SessionManager:
    """High-level session manager that persists user interactions and preferences."""

    def __init__(self, store: Optional[BaseSessionStore] = None) -> None:
        self.store = store or InMemoryStore()

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Return session data for the given id."""
        return self.store.get(session_id)

    def add_like(self, session_id: str, product: Dict[str, Any]) -> None:
        """Record a liked product and append it to the session history."""
        session = self.store.get(session_id)
        session["preferences"]["likes"].append(_slim(product))
        session["history"].append(
            {"type": "like", "item_id": product.get("id"), "ts": time.time()}
        )

    def add_dislike(self, session_id: str, product: Dict[str, Any]) -> None:
        """Record a disliked product and append it to the session history."""
        session = self.store.get(session_id)
        session["preferences"]["dislikes"].append(_slim(product))
        session["history"].append(
            {"type": "dislike", "item_id": product.get("id"), "ts": time.time()}
        )

    def set_trait(self, session_id: str, key: str, value: Any) -> None:
        """Set a single trait (e.g. preferred_color) in the session."""
        session = self.store.get(session_id)
        session["traits"][key] = value
