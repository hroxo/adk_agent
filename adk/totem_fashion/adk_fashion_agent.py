"""
Integration of Google ADK (Agent Development Kit) with the Totem Fashion Finder.

This module defines a Gemini-powered stylist agent using the ADK. The agent
wraps existing tools such as CatalogSearch, PreferenceStore and OutfitComposer,
allowing the LLM to decide when to call them. Note that `google-adk` and
`google-generativeai` must be installed in your Python environment for this
module to work.

Example usage (asynchronous):

    from totem_fashion.adk_fashion_agent import stylist_agent

    async def get_recommendation(session_id: str, message: str):
        async for event in stylist_agent.async_stream_query(user_id=session_id, message=message):
            print(event)

"""

from __future__ import annotations

try:
    # Import ADK components. These imports will succeed only if the google-adk
    # package is installed. Otherwise, ModuleNotFoundError will be raised.
    from google.adk.agents import LlmAgent
    from google.adk import tools as adk_tools
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "google-adk is not installed. Please add 'google-adk' and 'google-generativeai' "
        "to your requirements and install them before using the ADK agent."
    ) from exc

from typing import Any, Dict, Optional

from .tools.catalog_search import catalog_search
from .tools.outfit_composer import compose_outfit_from_seed
from .agent.session import SessionManager
from .tools.preference_store import PreferenceStoreTool
from .tools.data_loader import ITEMS


# Instantiate a session manager. In a multi-user environment you may want
# separate instances or a shared store (e.g. Firestore).
_session_manager = SessionManager()
_preference_store = PreferenceStoreTool(_session_manager)


def _like_product(session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
    """Register a product as liked in the session."""
    _preference_store.like(session_id, product)
    return {"status": "liked", "item_id": product.get("id")}


def _dislike_product(session_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
    """Register a product as disliked in the session."""
    _preference_store.dislike(session_id, product)
    return {"status": "disliked", "item_id": product.get("id")}


def _compose_outfit(session_id: str, seed_id: str, budget: Optional[float] = None) -> Dict[str, Any]:
    """Compose an outfit based on a seed product ID.

    Finds the product in the dataset by its id and delegates to
    `compose_outfit_from_seed`. Returns the outfit dict.
    """
    product = next((item for item in ITEMS if item.get("id") == seed_id), None)
    if not product:
        return {"error": f"Produto com id {seed_id} não encontrado"}
    return compose_outfit_from_seed(product, budget)


def _get_session_profile(session_id: str) -> Dict[str, Any]:
    """Return the entire session profile for inspection."""
    return _session_manager.get_session(session_id)


# Define tool wrappers for the ADK. Each tool must have a callable that
# accepts keyword arguments and returns a serializable result.
catalog_search_tool = adk_tools.Tool(
    name="CatalogSearch",
    func=catalog_search,
    description="Procura produtos no catálogo local. Parâmetros: query (string), category, color, gender, price_max, limit.",
)

like_tool = adk_tools.Tool(
    name="LikeProduct",
    func=_like_product,
    description="Regista um produto como gostado para a sessão actual. Requer session_id e o dicionário do produto.",
)

dislike_tool = adk_tools.Tool(
    name="DislikeProduct",
    func=_dislike_product,
    description="Regista um produto como não gostado para a sessão actual. Requer session_id e o dicionário do produto.",
)

outfit_tool = adk_tools.Tool(
    name="OutfitComposer",
    func=_compose_outfit,
    description="Gera um outfit completo a partir do ID de uma peça e um orçamento opcional.",
)

profile_tool = adk_tools.Tool(
    name="GetSessionProfile",
    func=_get_session_profile,
    description="Devolve as preferências e histórico de uma sessão dada.",
)


def create_stylist_agent(model_name: str = "gemini-2.5-pro") -> LlmAgent:
    """Factory function to create a Gemini-based stylist agent.

    Args:
        model_name: The Google Generative AI model to use (e.g. "gemini-1.0-pro").
    Returns:
        An instance of `LlmAgent` configured with our tools and instructions.
    """
    return LlmAgent(
        name="FashionStylistGemini",
        description=(
            "Um estilista virtual que usa LLMs da Google para sugerir roupas. "
            "Aprende os gostos do utilizador e propõe outfits completos."
        ),
        tools=[catalog_search_tool, like_tool, dislike_tool, outfit_tool, profile_tool],
        model=model_name,
        instruction=(
            "Sê um estilista virtual. Usa as ferramentas disponíveis para procurar roupas, "
            "registar gostos/desgostos, e compor outfits completos. Fornece respostas "
            "explicativas em português para o utilizador."
        ),
    )


# Create a default agent instance for convenience.  We default to the latest
# Gemini model (2.5 Pro) so that users benefit from improved reasoning and
# stylistic suggestions out of the box.  You can still pass a different model
# name to `create_stylist_agent()` if needed.
stylist_agent = create_stylist_agent()
