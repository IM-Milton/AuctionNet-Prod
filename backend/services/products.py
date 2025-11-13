from datetime import datetime, timezone
from dateutil.parser import isoparse
from typing import Optional

# All functions operate on YamlRepo injected from app

def _now_utc():
    return datetime.now(timezone.utc)

def _load_all(repo):
    return (
    repo.load("auctions"),
    repo.load("bids"),
    repo.load("users"),
    repo.load("products")
    )

def product_is_owned_by(repo, product_id: str, user_id: str) -> bool:
    products = repo.load("products").get("products", [])
    p = next((x for x in products if x["id"] == product_id), None)
    return bool(p and p.get("owner_id") == user_id)

def list_products(repo, owner_id: Optional[str] = None, category: Optional[str] = None, search: Optional[str] = None):
    auctions, bids, users, products = _load_all(repo)
    products = products.get("products", [])

    def match(p):
        if owner_id and p.get("owner_id") != owner_id:
            return False
        if category and p.get("category") != category:
            return False
        if search:
            s = search.lower()
            text = (p.get("title", "") + " " + p.get("description", "")).lower()
            return s in text
        return True

    out = []
    for p in products:
        if not match(p):
            continue
        out.append(p)
    return {"products": out}
    
def _find_user(users, uid):
    return next(u for u in users.get("users", []) if u["id"] == uid)