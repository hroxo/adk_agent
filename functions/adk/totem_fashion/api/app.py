from __future__ import annotations

import os
from fastapi import FastAPI, Query
from pydantic import BaseModel

# 1) Carrega .env em ambiente de desenvolvimento (ignora se não existir)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    # Sobe um nível: api/ -> totem_fashion/
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except Exception as e:
    print(f"⚠️  Não foi possível carregar .env: {e}")

# 2) (Opcional) Configurar Gemini via API key (local .env ou secret em Firebase)
try:
    import google.generativeai as genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except Exception:
    # Mantém a app a funcionar mesmo que a lib não esteja instalada
    pass

MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-pro")

from ..agent.agent import FashionStylistAgent

app = FastAPI(title="Totem Fashion Finder Agent API")

# Instância "global" do agente (podes trocar para DI se quiseres)
agent = FashionStylistAgent()


class ProductInput(BaseModel):
    """Pydantic model to validate product data from the client."""
    id: str
    name: str | None = None
    category: str | None = None
    color: str | None = None
    price: float | None = None
    brand: str | None = None
    image: str | None = None
    gender: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.get("/discover")
def discover(session_id: str, category: str | None = None):
    """Return items for the initial swipe deck."""
    return agent.discover(session_id=session_id, category=category)


@app.post("/swipe/like")
def swipe_like(session_id: str, product: ProductInput):
    """Record a like and return suggestions."""
    return agent.swipe_like(session_id=session_id, product=product.model_dump())


@app.post("/swipe/dislike")
def swipe_dislike(session_id: str, product: ProductInput):
    """Record a dislike and return suggestions."""
    return agent.swipe_dislike(session_id=session_id, product=product.model_dump())


@app.get("/outfit")
def get_outfit(
    session_id: str,
    seed_id: str,
    budget: float | None = Query(default=None, description="Optional budget for the outfit"),
):
    """Create a coordinated outfit from a seed item."""
    return agent.create_outfit_from_seed(session_id=session_id, seed_id=seed_id, budget=budget)

