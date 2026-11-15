"""Institutional Client Data Security, Encryption Vault & Privacy Compliance (GDPR).
Protects client PII, liquidity records, and API credentials using cryptographic standards.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from typing import Any, Dict, Optional


class ClientSecurityVault:
    """Handles cryptographic hashing, symmetric stream encryption, and secure data erasure."""

    def __init__(self, master_secret_key: Optional[str] = None) -> None:
        # In production, load master_secret_key from Cloud Environment Variables
        self._master_key = (master_secret_key or secrets.token_hex(32)).encode("utf-8")
        self._encrypted_store: Dict[str, str] = {}

    def hash_sensitive_id(self, plain_identifier: str) -> str:
        """Creates a salted PBKDF2-HMAC-SHA256 hash for client national IDs or passwords."""
        salt = hashlib.sha256(self._master_key).digest()[:16]
        dk = hashlib.pbkdf2_hmac("sha256", plain_identifier.encode("utf-8"), salt, 100_000)
        return dk.hex()

    def _derive_keystream(self, nonce: bytes, length: int) -> bytes:
        stream = bytearray()
        counter = 0
        while len(stream) < length:
            block = hmac.new(
                self._master_key,
                nonce + counter.to_bytes(4, "big"),
                hashlib.sha256,
            ).digest()
            stream.extend(block)
            counter += 1
        return bytes(stream[:length])

    def encrypt_client_record(self, client_id: str, payload: Dict[str, Any]) -> str:
        """Encrypts client financial and psychometric profile before storage."""
        raw_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        nonce = secrets.token_bytes(16)
        keystream = self._derive_keystream(nonce, len(raw_bytes))
        ciphertext = bytes(a ^ b for a, b in zip(raw_bytes, keystream))
        mac = hmac.new(self._master_key, nonce + ciphertext, hashlib.sha256).digest()

        token = base64.urlsafe_b64encode(nonce + mac + ciphertext).decode("ascii")
        self._encrypted_store[client_id] = token
        return token

    def decrypt_client_record(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Verifies integrity (HMAC) and decrypts client record for authorized sessions."""
        token = self._encrypted_store.get(client_id)
        if not token:
            return None

        raw = base64.urlsafe_b64decode(token.encode("ascii"))
        nonce, mac, ciphertext = raw[:16], raw[16:48], raw[48:]
        expected_mac = hmac.new(self._master_key, nonce + ciphertext, hashlib.sha256).digest()

        if not hmac.compare_digest(mac, expected_mac):
            raise SecurityError("Data integrity check failed! Possible tampering detected.")

        keystream = self._derive_keystream(nonce, len(ciphertext))
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, keystream))
        return json.loads(plaintext.decode("utf-8"))

    def purge_client_data(self, client_id: str) -> bool:
        """GDPR Right-to-be-Forgotten: Permanently wipes client encrypted records."""
        if client_id in self._encrypted_store:
            del self._encrypted_store[client_id]
            return True
        return False


class SecurityError(Exception):
    """Raised when cryptographic integrity or access validation fails."""
