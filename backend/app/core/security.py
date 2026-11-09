"""Funciones de seguridad para contraseñas y tokens de acceso."""

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt


_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def hash_password(password: str) -> str:
    """Guarda un hash scrypt con sal aleatoria; nunca almacena texto plano."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=64,
    )
    salt_text = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_text = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt_text}${digest_text}"


def verify_password(password: str, encoded_hash: str | None) -> bool:
    """Compara una contraseña con su hash usando comparación de tiempo constante."""
    if not encoded_hash:
        return False
    try:
        if encoded_hash.startswith("scrypt:"):
            # Compatibilidad con hashes Werkzeug: scrypt:N:r:p$salt$hex_digest.
            method, salt_text, digest_text = encoded_hash.split("$", 2)
            algorithm, n_text, r_text, p_text = method.split(":", 3)
            if algorithm != "scrypt":
                return False
            n, r, p = int(n_text), int(r_text), int(p_text)
            expected = bytes.fromhex(digest_text)
            actual = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt_text.encode("utf-8"),
                n=n,
                r=r,
                p=p,
                dklen=len(expected),
                maxmem=128 * 1024 * 1024,
            )
            return hmac.compare_digest(actual, expected)
        algorithm, n_text, r_text, p_text, salt_text, expected_text = encoded_hash.split("$", 5)
        if algorithm != "scrypt":
            return False
        if (int(n_text), int(r_text), int(p_text)) != (_SCRYPT_N, _SCRYPT_R, _SCRYPT_P):
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(expected_text.encode("ascii"))
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n_text),
            r=int(r_text),
            p=int(p_text),
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, UnicodeError):
        return False


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY debe tener al menos 32 caracteres.")
    return secret


def create_access_token(account_id: int) -> str:
    minutes = int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60"))
    if minutes < 1:
        raise RuntimeError("JWT_ACCESS_TOKEN_MINUTES debe ser mayor que cero.")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(account_id),
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def read_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None
