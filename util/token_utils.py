import hmac
import hashlib
import secrets
import time
import uuid
import base64
import json


def generate_token(length: int = 32) -> str:
    return secrets.token_hex(length)


def generate_urlsafe_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_signed_token(payload: dict, secret: str, expires_in: int | None = None) -> str:
    if expires_in:
        payload = {**payload, "exp": int(time.time()) + expires_in}
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{sig}"


def verify_signed_token(token: str, secret: str) -> dict | None:
    try:
        encoded, sig = token.rsplit(".", 1)
        expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(encoded).decode())
        if "exp" in payload and time.time() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


if __name__ == "__main__":
    print("token:        ", generate_token(16))
    print("urlsafe:      ", generate_urlsafe_token(16))
    print("uuid:         ", generate_uuid())
    print("short_id:     ", generate_short_id())
    print("hashed:       ", hash_token("my-secret-token"))

    secret = "super-secret-key"
    signed = create_signed_token({"user_id": 42, "role": "admin"}, secret, expires_in=60)
    print("\nsigned token: ", signed)

    payload = verify_signed_token(signed, secret)
    print("verified:     ", payload)

    tampered = signed[:-4] + "xxxx"
    print("tampered:     ", verify_signed_token(tampered, secret))
