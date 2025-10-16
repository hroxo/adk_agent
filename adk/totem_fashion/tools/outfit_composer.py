# tools/outfit_composer.py
from typing import Dict, Any, List, Optional
from .catalog_search import catalog_search

# Mapeamento simplificado de categorias para combinações. Ajusta conforme preferires.
_COMPLEMENT = {
    "Casaco Bomber": ["Camisola de Malha", "Calças de Ganga Skinny", "Calças de Ganga Wide Leg"],
    "Camisola de Malha": ["Calças de Ganga Skinny", "Calças Marine", "Casaco Bomber"],
    "Pijama Polar de Natal": ["Pijama Polar de Natal"],
    # acrescenta mapeamentos para outras categorias
}

def _harmonize_colors(color: str) -> List[str]:
    """
    Um mini-mapa de paletas; retorna possíveis cores complementares.
    Exemplo básico; podes expandir conforme o catálogo crescer.
    """
    palette = {
        "bege": ["castanho", "branco", "bege claro"],
        "cinzento escuro": ["preto", "branco", "rosa"],
        "verde": ["preto", "bege", "branco"],
        "multicor": [],  # neutro
        "branco": ["preto", "bege", "azul escuro"],
        # etc.
    }
    return palette.get(color.lower(), [])

def compose_outfit_from_seed(seed: Dict[str, Any], budget: Optional[float] = None) -> Dict[str, Any]:
    seed_cat = seed.get("category")
    seed_color = seed.get("color")
    # Selecciona categorias sugeridas (ou busca todas excepto a da peça)
    target_cats = _COMPLEMENT.get(seed_cat, [])
    if not target_cats:
        # fallback: todas as categorias excepto a original
        from .data_loader import ITEMS
        target_cats = sorted(set(i["category"] for i in ITEMS if i["category"] != seed_cat))[:3]

    # Selecciona cores compatíveis
    colors = _harmonize_colors(seed_color) or [seed_color]

    outfit: List[Dict[str, Any]] = [seed]
    total_price = seed.get("price", 0.0)

    for cat in target_cats:
        # procura uma peça da categoria que combine na cor e orçamento
        options = catalog_search(category=cat, color=colors[0], limit=5)
        if not options:
            options = catalog_search(category=cat, limit=5)
        candidate = options[0] if options else None
        if candidate:
            # verifica orçamento
            if budget and total_price + candidate["price"] > budget:
                continue
            outfit.append(candidate)
            total_price += candidate["price"]

    return {
        "items": outfit,
        "total_price": round(total_price, 2),
        "explanation": f"Look criado a partir de '{seed['name']}' (categoria {seed_cat}) e cores compatíveis.",
    }
