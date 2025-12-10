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

def list_auctions(repo, status: Optional[str] = None,
                  category: Optional[str] = None,
                  search: Optional[str] = None,
                  condition: Optional[str] = None):
    auctions, bids, users, products = _load_all(repo)
    auctions_list = auctions.get("auctions", [])
    products_list = products.get("products", [])
    users_list = users.get("users", [])
    prod_map = {p["id"]: p for p in products_list}
    user_map = {u["id"]: u for u in users_list}

    out: List[Dict[str, Any]] = []
    for a in auctions_list:
        p = prod_map.get(a["product_id"])
        if not p:
            continue

        # Filtres (optionnels)
        if status and a.get("status") != status:
            continue
        if category and p.get("category") != category:
            continue
        if condition and p.get("condition") != condition:
            continue
        if search:
            s = search.lower()
            if s not in p.get("title", "").lower() and s not in p.get("description", "").lower():
                continue

        # Ajouter le nom du gagnant si l'enchère est terminée
        winner_username = None
        if a.get("winner_id"):
            winner = user_map.get(a["winner_id"])
            if winner:
                winner_username = winner.get("username", winner.get("email", "").split("@")[0])

        # ⚠️ NE PAS convertir les dates ici
        out.append({**a, "product": p, "winner_username": winner_username})

    return {"auctions": out}


    def match(a):
        if status and a.get("status") != status:
            return False
        prod = products_map.get(a["product_id"]) or {}
        if category and prod.get("category") != category:
            return False
        if search:
            s = search.lower()
            text = (prod.get("title", "") + " " + prod.get("description", "")).lower()
            return s in text
        return True

    out = []
    for a in auctions:
        if not match(a):
            continue
        prod = products_map.get(a["product_id"], {})
        out.append({**a, "product": prod})
    return {"auctions": out}

def get_auction(repo, auction_id: str):
    auctions = repo.load("auctions").get("auctions", [])
    bids = repo.load("bids").get("bids", [])
    products = repo.load("products").get("products", [])
    users = repo.load("users").get("users", [])
    prod_map = {p["id"]: p for p in products}
    user_map = {u["id"]: u for u in users}
    a = next((x for x in auctions if x["id"] == auction_id), None)
    if not a:
        return None
    
    # Compter le nombre d'enchères (bids) pour cette enchère
    bids_count = len([b for b in bids if b["auction_id"] == auction_id])
    
    # Ajouter le nom du gagnant si l'enchère est terminée
    winner_username = None
    if a.get("winner_id"):
        winner = user_map.get(a["winner_id"])
        if winner:
            winner_username = winner.get("username", winner.get("email", "").split("@")[0])
    
    return {**a, "product": prod_map.get(a["product_id"]), "bids_count": bids_count, "winner_username": winner_username}


def create_auction(repo, payload):
    doc = repo.load("auctions")
    items = doc.get("auctions", [])
    new_id = repo.next_id(doc, "auctions", prefix="a_")

    items.append({
        "id": new_id,
        "product_id": payload.product_id,
        "start_price": float(payload.start_price),
        "min_increment": float(getattr(payload, "min_increment", 50)),
        "start_at": payload.start_at,   
        "end_at": payload.end_at,
        "status": "scheduled",
        "current_price": float(payload.start_price),
        "current_bid_id": None,
    })

    repo.save("auctions", {"auctions": items})
    return get_auction(repo, new_id)


    start_at = isoparse(payload.start_at)
    end_at = isoparse(payload.end_at)
    if end_at <= start_at:
        raise ValueError("end_at must be after start_at")

    new_id = repo.next_id(auctions_doc, "auctions", prefix="a_")
    auction = {
        "id": new_id,
        "product_id": payload.product_id,
        "start_price": float(payload.start_price),
        "start_at": start_at.astimezone(timezone.utc).isoformat(),
        "end_at": end_at.astimezone(timezone.utc).isoformat(),
        "status": "scheduled",
        "current_price": float(payload.start_price),
        "current_bid_id": None,
        "min_increment": float(payload.min_increment),
    }
    auctions_doc.setdefault("auctions", []).append(auction)
    repo.save("auctions", auctions_doc)
    return auction
    
def _find_user(users, uid):
    return next(u for u in users.get("users", []) if u["id"] == uid)

def _find_bid(bids, bid_id):
    return next((b for b in bids.get("bids", []) if b["id"] == bid_id), None)
    
def place_bid(repo, auction_id: str, user_id: str, amount: float):
    auctions_doc, bids_doc, users_doc, products_doc = _load_all(repo)

    auction = next(a for a in auctions_doc.get("auctions", []) if a["id"] == auction_id)

    # status & time guards
    now = _now_utc()
    if auction["status"] != "running":
        raise ValueError("Auction not running")
    if isoparse(auction["end_at"]).astimezone(timezone.utc) <= now:
        raise ValueError("Auction already ended")

    if amount < auction["current_price"] + auction["min_increment"]:
        raise ValueError("Bid too low")

    # prevent self-bid
    product = next(p for p in products_doc.get("products", []) if p["id"] == auction["product_id"])
    if product.get("owner_id") == user_id:
        raise ValueError("Owner cannot bid on own product")
    
    user = _find_user(users_doc, user_id)
    available = user.get("balance", 0.0) - user.get("held", 0.0)
    if amount > available:
        raise ValueError("Insufficient funds (available < amount)")
    
    # Release previous leader hold
    if auction.get("current_bid_id"):
        old_bid = _find_bid(bids_doc, auction["current_bid_id"])
        if old_bid:
            old_user = _find_user(users_doc, old_bid["user_id"])
            old_user["held"] = float(old_user.get("held", 0.0)) - float(old_bid["amount"])

    # Create new bid
    bid_id = repo.next_id(bids_doc, "bids", prefix="b_")
    new_bid = {
        "id": bid_id,
        "auction_id": auction_id,
        "user_id": user_id,
        "amount": float(amount),
        "placed_at": now.isoformat()
        }
    bids_doc.setdefault("bids", []).append(new_bid)

    # Reserve funds for new leader
    user["held"] = float(user.get("held", 0.0)) + float(amount)

    auction["current_price"] = float(amount)
    auction["current_bid_id"] = bid_id

    repo.save("bids", bids_doc)
    repo.save("users", users_doc)
    repo.save("auctions", auctions_doc)

    return {"ok": True, "bid_id": bid_id, "current_price": auction["current_price"]}

def open_auction_if_due(repo, auction_id: str):
    auctions_doc = repo.load("auctions")
    auction = next((a for a in auctions_doc.get("auctions", []) if a["id"] == auction_id), None)
    if not auction:
        return
    if auction["status"] != "scheduled":
        return
    if isoparse(auction["start_at"]).astimezone(timezone.utc) <= _now_utc():
        auction["status"] = "running"
        repo.save("auctions", auctions_doc)

def close_auction_if_due(repo, auction_id: str):
    auctions_doc, bids_doc, users_doc, products_doc = _load_all(repo)
    a = next((x for x in auctions_doc.get("auctions", []) if x["id"] == auction_id), None)
    if not a:
        return
    if a["status"] == "closed":
        return
    if isoparse(a["end_at"]).astimezone(timezone.utc) <= _now_utc():
        a["status"] = "closed"
        if a.get("current_bid_id"):
            win = next(b for b in bids_doc.get("bids", []) if b["id"] == a["current_bid_id"])
            buyer = next(u for u in users_doc.get("users", []) if u["id"] == win["user_id"])
            # Débiter le compte et ajouter l'achat
            buyer["held"] = float(buyer.get("held", 0.0)) - float(win["amount"])
            buyer["balance"] = float(buyer.get("balance", 0.0)) - float(win["amount"])
            buyer.setdefault("purchases", []).append(a["product_id"])
            # Ajouter le winner_id à l'enchère
            a["winner_id"] = win["user_id"]
        # Save
        repo.save("users", users_doc)
        repo.save("auctions", auctions_doc)