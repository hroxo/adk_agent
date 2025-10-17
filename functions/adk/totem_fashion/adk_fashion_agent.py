# adk/totem_fashion/adk_fashion_agent.py
from __future__ import annotations
import os
from typing import Dict, Any, List

# Importa o ADK
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# Configura o Gemini localmente (apenas se GEMINI_API_KEY estiver no .env ou secret)
try:
    import google.generativeai as genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except Exception:
    pass

MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-pro")

# Importa funções que vão ser expostas como ferramentas
from .agent.agent import FashionStylistAgent
from .tools.catalog_search import catalog_search

def like_product(session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
    return FashionStylistAgent().swipe_like(session_id, product)

def dislike_product(session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
    return FashionStylistAgent().swipe_dislike(session_id, product)

def compose_outfit(session_id: str, seed_id: str, budget: float | None = None) -> Dict[str, Any]:
    return FashionStylistAgent().create_outfit_from_seed(session_id, seed_id, budget)

def create_stylist_agent(model_name: str | None = None) -> LlmAgent:
    model = model_name or MODEL_NAME
    tools: List[FunctionTool] = [
        FunctionTool.from_fn(
            catalog_search,
            name="CatalogSearch",
            description="Procura no catálogo produtos que combinem com as preferências",
        ),
        FunctionTool.from_fn(
            like_product,
            name="LikeProduct",
            description="Regista um like e actualiza as preferências",
        ),
        FunctionTool.from_fn(
            dislike_product,
            name="DislikeProduct",
            description="Regista um dislike e actualiza as preferências",
        ),
        FunctionTool.from_fn(
            compose_outfit,
            name="OutfitComposer",
            description="Cria um outfit completo a partir de uma peça de partida",
        ),
    ]
    system_prompt = (
        "És um estilista virtual. Usa as ferramentas disponíveis para "
        "perceber o gosto do utilizador e compor outfits que harmonizem cor, estação e orçamento."
    )
    return LlmAgent(name="FashionStylist", tools=tools, system_prompt=system_prompt, model=model)

