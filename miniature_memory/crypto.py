from __future__ import annotations

import base64
import os
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

KDF_ITERATIONS = 390_000
SALT_SIZE = 16


class MissingPassphraseError(RuntimeError):
    pass


class CryptoManager:
    def __init__(self, salt_file: Path, passphrase: str) -> None:
        if not passphrase:
            raise MissingPassphraseError(
                "Passphrase missing. Set MINI_MEMORY_PASSPHRASE in your environment."
            )
        self.salt_file = salt_file
        self.passphrase = passphrase.encode("utf-8")
        self.salt = self._load_or_create_salt()
        self.fernet = Fernet(self._derive_key())

    def _load_or_create_salt(self) -> bytes:
        if self.salt_file.exists():
            return self.salt_file.read_bytes()
        salt = os.urandom(SALT_SIZE)
        self.salt_file.write_bytes(salt)
        try:
            os.chmod(self.salt_file, 0o600)
        except PermissionError:
            pass
        return salt

    def _derive_key(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=KDF_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.passphrase))

    def encrypt(self, plaintext: bytes) -> bytes:
        return self.fernet.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.fernet.decrypt(ciphertext)
