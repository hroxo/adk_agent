# agent/session.py
from typing import Any, Dict, Optional
import time

class BaseSessionStore:
    def get(self, session_id: str) -> Dict[str, Any]: ...
    def put(self, session_id: str, data: Dict[str, Any]) -> None: ...
    def update(self, session_id: str, patch: Dict[str, Any]) -> None: ...

class InMemoryStore(BaseSessionStore):
    def __init__(self):
        self._mem: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        return self._mem.setdefault(session_id, {
            "created_at": time.time(),
            "preferences": {"likes": [], "dislikes": []},
            "traits": {},  # cor preferida, estilos, etc.
            "history": [], # items vistos/aceites
        })

    def put(self, session_id: str, data: Dict[str, Any]) -> None:
        self._mem[session_id] = data

    def update(self, session_id: str, patch: Dict[str, Any]) -> None:
        base = self.get(session_id)
        # merge superficial:
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k].update(v)
            else:
                base[k] = v

class SessionManager:
    def __init__(self, store: Optional[BaseSessionStore] = None):
        self.store = store or InMemoryStore()

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self.store.get(session_id)

    def add_like(self, session_id: str, product: Dict[str, Any]) -> None:
        s = self.store.get(session_id)
        s["preferences"]["likes"].append(_slim(product))
        s["history"].append({"type": "like", "item_id": product["id"], "ts": time.time()})

    def add_dislike(self, session_id: str, product: Dict[str, Any]) -> None:
        s = self.store.get(session_id)
        s["preferences"]["dislikes"].append(_slim(product))
        s["history"].append({"type": "dislike", "item_id": product["id"], "ts": time.time()})

    def set_trait(self, session_id: str, key: str, value: Any) -> None:
        s = self.store.get(session_id)
        s["traits"][key] = value

def _slim(p: Dict[str, Any]) -> Dict[str, Any]:
    # guarda só o essencial
    return {
        "id": p.get("id"),
        "name": p.get("name"),
        "category": p.get("category"),
        "color": p.get("color"),
        "price": p.get("price"),
    }

