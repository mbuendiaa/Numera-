import base64
import hashlib
import hmac
import os

_PBKDF2_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """Hash a password with bcrypt when available, otherwise PBKDF2-SHA256."""
    try:
        import bcrypt  # type: ignore

        return "bcrypt$" + bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
        )
        return "pbkdf2_sha256${}${}${}".format(
            _PBKDF2_ITERATIONS,
            base64.urlsafe_b64encode(salt).decode(),
            base64.urlsafe_b64encode(digest).decode(),
        )


def verify_password(password: str, encoded: str) -> bool:
    if encoded.startswith("bcrypt$"):
        try:
            import bcrypt  # type: ignore
        except ImportError:
            return False
        return bcrypt.checkpw(password.encode(), encoded.removeprefix("bcrypt$").encode())

    try:
        algorithm, iterations, salt_b64, digest_b64 = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError):
        return False
