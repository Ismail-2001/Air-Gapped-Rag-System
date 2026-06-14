import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


_AES_KEY_SALT = b"FortalezaDigital_AESv1"


def derive_key(master_key: str, salt: bytes = _AES_KEY_SALT) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_key.encode()))


def encrypt_bytes(data: bytes, master_key: str) -> bytes:
    key = derive_key(master_key)
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_bytes(token: bytes, master_key: str) -> bytes:
    key = derive_key(master_key)
    f = Fernet(key)
    return f.decrypt(token)


def encrypt_file(src_path: str, dst_path: str | None = None, master_key: str | None = None):
    if master_key is None:
        master_key = os.environ.get("FORTALEZA_ENCRYPTION_KEY", "")
        if not master_key:
            raise ValueError("FORTALEZA_ENCRYPTION_KEY not set")
    with open(src_path, "rb") as f:
        data = f.read()
    enc = encrypt_bytes(data, master_key)
    dst = dst_path or src_path + ".enc"
    with open(dst, "wb") as f:
        f.write(enc)
    return dst


def decrypt_file(src_path: str, dst_path: str | None = None, master_key: str | None = None):
    if master_key is None:
        master_key = os.environ.get("FORTALEZA_ENCRYPTION_KEY", "")
        if not master_key:
            raise ValueError("FORTALEZA_ENCRYPTION_KEY not set")
    with open(src_path, "rb") as f:
        data = f.read()
    dec = decrypt_bytes(data, master_key)
    dst = dst_path or src_path.removesuffix(".enc")
    with open(dst, "wb") as f:
        f.write(dec)
    return dst


def generate_key() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "genkey":
        print(generate_key())
    elif action == "encrypt":
        encrypt_file(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        print("Encrypted.")
    elif action == "decrypt":
        decrypt_file(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        print("Decrypted.")
    else:
        print("Usage: python crypto.py <genkey|encrypt <src> [dst]|decrypt <src> [dst]>")
