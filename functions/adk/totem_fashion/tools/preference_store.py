"""
Preference store tool for the Fashion Finder agent.

This module wraps the SessionManager to provide simple functions that can be
exposed to an agent or API to record likes and dislikes, and to retrieve the
current profile.
"""

from __future__ import annotations

from typing import Any, Dict

from ..agent.session import SessionManager


class PreferenceStoreTool:
    """Encapsulates preferences operations for the agent."""

    def __init__(self, session_manager: SessionManager) -> None:
        self.sm = session_manager

    def like(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """Record a like for a product and return a simple acknowledgement."""
        self.sm.add_like(session_id, product)
        return {"ok": True}

    def dislike(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """Record a dislike for a product and return a simple acknowledgement."""
        self.sm.add_dislike(session_id, product)
        return {"ok": True}

    def get_profile(self, session_id: str) -> Dict[str, Any]:
        """Return the entire session data for a given session id."""
        return self.sm.get_session(session_id)
