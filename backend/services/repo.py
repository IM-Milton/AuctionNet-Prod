from pathlib import Path
import os
import fcntl
import tempfile
from typing import Any, Dict
from ruamel.yaml import YAML
yaml = YAML()
DB_DIR = Path(os.environ.get("DB_DIR", "/data/db"))


class YamlRepo:
    def __init__(self):
        DB_DIR.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return DB_DIR / f"{name}.yaml"


    def load(self, name: str) -> Dict[str, Any]:
        p = self._path(name)
        if not p.exists():
            return {}
        with open(p, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = yaml.load(f) or {}
            fcntl.flock(f, fcntl.LOCK_UN)
            return data


    def save(self, name: str, data: Dict[str, Any]):
        p = self._path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", delete=False, dir=p.parent) as tmp:
            yaml.dump(data, tmp)
            tmp.flush(); os.fsync(tmp.fileno())
            tmp_path = tmp.name
        os.replace(tmp_path, p)


    def next_id(self, root: Dict[str, Any], key: str, prefix: str) -> str:
        arr = root.get(key, [])
        return f"{prefix}{len(arr)+1}"




def ensure_default_data(repo: YamlRepo):
    # categories
    categories = repo.load("categories")
    if not categories:
        repo.save("categories", {"categories": [
            "vehicule", "immobilier", "electronique", "art", "autre"
        ]})


    # users
    users = repo.load("users")
    if not users:
        repo.save("users", {"users": []})


    # products
    products = repo.load("products")
    if not products:
        repo.save("products", {"products": []})


    # auctions
    auctions = repo.load("auctions")
    if not auctions:
        repo.save("auctions", {"auctions": []})


    # bids
    bids = repo.load("bids")
    if not bids:
        repo.save("bids", {"bids": []})