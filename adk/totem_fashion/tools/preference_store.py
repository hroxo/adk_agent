# tools/preference_store.py
from typing import Dict, Any
from agent.session import SessionManager

class PreferenceStoreTool:
    def __init__(self, session_manager: SessionManager):
        self.sm = session_manager

    def like(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        self.sm.add_like(session_id, product)
        return {"ok": True}

    def dislike(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        self.sm.add_dislike(session_id, product)
        return {"ok": True}

    def get_profile(self, session_id: str) -> Dict[str, Any]:
        return self.sm.get_session(session_id)
