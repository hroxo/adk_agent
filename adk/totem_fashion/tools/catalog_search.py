# tools/catalog_search.py
from typing import List, Dict, Any, Optional
from .data_loader import ITEMS

def catalog_search(
    query: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    gender: Optional[str] = None,
    price_max: Optional[float] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Filtra a lista ITEMS (carregada de db_preco.json) com base nos parâmetros recebidos.
    """
    results = ITEMS.copy()

    if query:
        q = query.lower()
        results = [item for item in results
                   if q in item["name"].lower() or q in item["category"].lower() or q in item["brand"].lower()]

    if category:
        results = [item for item in results if item["category"].lower() == category.lower()]

    if color:
        # permite procurar por cores compostas (ex. "cinzento escuro" contém "cinzento")
        c = color.lower()
        results = [item for item in results if c in item["color"].lower()]

    if gender:
        results = [item for item in results if item["gender"].lower() == gender.lower()]

    if price_max is not None:
        results = [item for item in results if item["price"] <= price_max]

    return results[:limit]
