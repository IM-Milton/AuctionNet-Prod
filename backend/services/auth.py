from werkzeug.security import generate_password_hash, check_password_hash as _check


def hash_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(password: str, hashed: str) -> bool:
    return _check(hashed, password)

def ensure_user_uniqueness(users_doc, email: str):
    if any(u["email"] == email for u in users_doc.get("users", [])):
        raise ValueError("Email already registered")