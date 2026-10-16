"""Passwords and sign-in tokens (stdlib only, no extra packages).

Roles:
  owner     vehicle owner (every user story in the proposal)
  mechanic  contributes advice notes, which an admin must approve before use
  admin     manages manuals, reviews mechanic notes, assigns roles, sees usage stats
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

ROLES = ("owner", "mechanic", "admin")
TOKEN_TTL_S = 7 * 24 * 3600
_ITER = 240_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITER)
    return f"pbkdf2_sha256${_ITER}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt, digest = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iters))
        return hmac.compare_digest(dk.hex(), digest)
    except (ValueError, TypeError):
        return False


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def secret_key() -> bytes:
    key = os.getenv("AUTOCARE_SECRET_KEY")
    if key:
        return key.encode()
    # Dev fallback: stable per machine so restarts don't sign everyone out.
    path = os.path.join(os.path.dirname(__file__), "..", ".secret_key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    with open(path) as f:
        return f.read().strip().encode()


def make_token(user_id: str, role: str, key: bytes | None = None, ttl_s: int = TOKEN_TTL_S) -> str:
    payload = _b64(json.dumps({"sub": user_id, "role": role, "exp": int(time.time()) + ttl_s}).encode())
    sig = _b64(hmac.new(key or secret_key(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def read_token(token: str, key: bytes | None = None) -> dict | None:
    """Return {"sub", "role", "exp"} if the token is genuine and unexpired, else None."""
    try:
        payload, sig = token.split(".")
        good = _b64(hmac.new(key or secret_key(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, good):
            return None
        data = json.loads(_unb64(payload))
        if data.get("exp", 0) < time.time() or data.get("role") not in ROLES:
            return None
        return data
    except (ValueError, json.JSONDecodeError):
        return None
