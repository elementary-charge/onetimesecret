import string
import hashlib
import base64

import nanoid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet


_SECRET_KEY_ALPHABET = string.ascii_letters + string.digits
_password_hasher = PasswordHasher()


DEFAULT_PASSPHRASE_HASH = _password_hasher.hash('')


def generate_secret_key() -> str:
    return nanoid.generate(alphabet=_SECRET_KEY_ALPHABET)


def hash_passphrase(passphrase: str) -> str:
    return _password_hasher.hash(passphrase)


def verify_passphrase(passphrase_hash: str, passphrase: str) -> bool:
    try:
        _password_hasher.verify(passphrase_hash, passphrase)
        return True
    except VerifyMismatchError:
        pass
    return False


def _build_fernet_key(passphrase: str) -> bytes:
    return base64.b64encode(hashlib.sha256(passphrase.encode()).digest()[:32])


def encrypt_secret(secret: str, passphrase: str) -> str:
    key = _build_fernet_key(passphrase)
    return Fernet(key).encrypt(secret.encode()).decode()


def decrypt_secret(secret_hash: str, passphrase: str) -> str:
    key = _build_fernet_key(passphrase)
    return Fernet(key).decrypt(secret_hash.encode()).decode()
