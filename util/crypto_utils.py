import hashlib
import hmac
import secrets
import base64
import os


def hash_md5(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


def hash_sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def hash_sha512(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha512(data).hexdigest()


def generate_salt(length: int = 32) -> bytes:
    return os.urandom(length)


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = generate_salt()
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations=260_000)
    return key.hex(), salt.hex()


def verify_password(password: str, hashed: str, salt_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    key, _ = hash_password(password, salt)
    return hmac.compare_digest(key, hashed)


def hmac_sign(message: str, secret: str) -> str:
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def hmac_verify(message: str, signature: str, secret: str) -> bool:
    expected = hmac_sign(message, secret)
    return hmac.compare_digest(expected, signature)


def encode_base64(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).decode()


def decode_base64(data: str) -> str:
    return base64.urlsafe_b64decode(data).decode()


def xor_encrypt(text: str, key: str) -> str:
    key_bytes = (key * (len(text) // len(key) + 1)).encode()
    encrypted = bytes(a ^ b for a, b in zip(text.encode(), key_bytes))
    return encode_base64(encrypted)


def xor_decrypt(token: str, key: str) -> str:
    encrypted = base64.urlsafe_b64decode(token)
    key_bytes = (key * (len(encrypted) // len(key) + 1)).encode()
    return bytes(a ^ b for a, b in zip(encrypted, key_bytes)).decode()


if __name__ == "__main__":
    print("md5:        ", hash_md5("hello"))
    print("sha256:     ", hash_sha256("hello"))
    print("sha512:     ", hash_sha512("hello")[:40] + "...")

    hashed, salt = hash_password("my_secret_password")
    print("\nhashed pw:  ", hashed[:40] + "...")
    print("verify ok:  ", verify_password("my_secret_password", hashed, salt))
    print("verify bad: ", verify_password("wrong_password", hashed, salt))

    sig = hmac_sign("hello world", "secret_key")
    print("\nhmac sig:   ", sig)
    print("hmac verify:", hmac_verify("hello world", sig, "secret_key"))
    print("hmac tamper:", hmac_verify("hello world!", sig, "secret_key"))

    encoded = encode_base64("Hello, World!")
    print("\nbase64:     ", encoded)
    print("decoded:    ", decode_base64(encoded))

    token = xor_encrypt("secret message", "mykey")
    print("\nxor enc:    ", token)
    print("xor dec:    ", xor_decrypt(token, "mykey"))
