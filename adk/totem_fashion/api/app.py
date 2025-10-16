# api/app.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
from agent.agent import FashionStylistAgent

app = FastAPI(title="Totem Fashion Finder Agent API")
agent = FashionStylistAgent()

class Product(BaseModel):
    id: str
    name: str | None = None
    category: str | None = None
    color: str | None = None
    price: float | None = None
    image: str | None = None

@app.get("/discover")
def discover(session_id: str, category: str | None = None):
    return agent.discover(session_id, category)

@app.post("/swipe/like")
def swipe_like(session_id: str, product: Product):
    return agent.swipe_like(session_id, product.dict())

@app.post("/swipe/dislike")
def swipe_dislike(session_id: str, product: Product):
    return agent.swipe_dislike(session_id, product.dict())

@app.get("/outfit")
def outfit(session_id: str, seed_id: str, budget: float | None = Query(default=None)):
    return agent.create_outfit_from_seed(session_id, seed_id, budget)
