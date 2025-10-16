# tools/data_loader.py
import json
import os
from typing import List, Dict, Any

# Caminho por omissão; podes usar uma variável de ambiente para customizar
DATA_FILE = os.getenv("DATA_FILE", os.path.join(os.path.dirname(__file__), "..", "db_preco.json"))

def load_items() -> List[Dict[str, Any]]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Lê tudo uma vez para memória
ITEMS: List[Dict[str, Any]] = load_items()

