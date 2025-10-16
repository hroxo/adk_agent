# agent/agent.py
from typing import Dict, Any, List, Optional
from agent.session import SessionManager
from tools.catalog_search import catalog_search
from tools.preference_store import PreferenceStoreTool
from tools.outfit_composer import compose_outfit_from_seed
from tools.history_recall import infer_traits_from_history  # opcional

class FashionStylistAgent:
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.sm = session_manager or SessionManager()
        self.prefs = PreferenceStoreTool(self.sm)

    def discover(self, session_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return catalog_search(category=category, limit=30)

    def swipe_like(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        self.prefs.like(session_id, product)
        return self._recommend_from_profile(session_id)

    def swipe_dislike(self, session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        self.prefs.dislike(session_id, product)
        return self._recommend_from_profile(session_id)

    def create_outfit_from_seed(self, session_id: str, seed_id: str, budget: Optional[float] = None) -> Dict[str, Any]:
        seed = self._get_product_by_id(seed_id)
        return compose_outfit_from_seed(seed, budget)

    def _recommend_from_profile(self, session_id: str) -> Dict[str, Any]:
        s = self.sm.get_session(session_id)
        traits = infer_traits_from_history(s)  # se não quiseres memória longa, remove esta linha
        color = traits.get("preferred_color")
        picks = catalog_search(color=color, limit=12) if color else catalog_search(limit=12)
        return {
            "suggestions": picks,
            "hint": f"Baseado na tua preferência por {color}" if color else "Baseado nas tuas interacções recentes"
        }

    def _get_product_by_id(self, pid: str) -> Dict[str, Any]:
        from tools.data_loader import ITEMS
        for item in ITEMS:
            if item["id"] == pid:
                return item
        raise ValueError(f"Produto com id {pid} não encontrado")
