from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def verify_ed25519_signature(
    public_key_hex: str, message: str, signature_hex: str
) -> bool:
    """Verify an Ed25519 signature against a message and public key.

    Args:
        public_key_hex: Hex-encoded Ed25519 public key (32 bytes).
        message: The original message that was signed (UTF-8 string).
        signature_hex: Hex-encoded Ed25519 signature (64 bytes).

    Returns:
        bool: True if signature is cryptographically valid, False otherwise.
    """
    try:
        pk_bytes = bytes.fromhex(public_key_hex)
        sig_bytes = bytes.fromhex(signature_hex)
        msg_bytes = message.encode("utf-8")

        public_key = Ed25519PublicKey.from_public_bytes(pk_bytes)
        public_key.verify(sig_bytes, msg_bytes)
        return True
    except (InvalidSignature, ValueError) as e:
        print(f"Failed signature check: {e}")
        return False
