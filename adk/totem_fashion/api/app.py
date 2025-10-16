"""
FastAPI application exposing the Fashion Stylist agent.

This module defines the web API endpoints that the mirror frontend can call to
interact with the underlying agent. The API is intentionally simple and
stateless except for the session_id passed by the client.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from ..agent.agent import FashionStylistAgent


app = FastAPI(title="Totem Fashion Finder Agent API")

# Global agent instance (would be dependency-injected in a larger app)
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
    """Compose an outfit from a seed product id."""
    try:
        return agent.create_outfit_from_seed(session_id=session_id, seed_id=seed_id, budget=budget)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
