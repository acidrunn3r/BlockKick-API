import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from app.core.crypto import verify_ed25519_signature


def make_keypair(message: str) -> tuple[str, str]:
    """Return (public_key_hex, signature_hex) for the given message."""
    private_key = Ed25519PrivateKey.generate()
    public_key_hex = (
        private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    )
    signature_hex = private_key.sign(message.encode()).hex()
    return public_key_hex, signature_hex


@pytest.mark.unit
class TestVerifyEd25519Signature:
    def test_valid_signature_returns_true(self):
        message = "sign-this-nonce"
        pub, sig = make_keypair(message)
        assert verify_ed25519_signature(pub, message, sig) is True

    def test_wrong_message_returns_false(self):
        pub, sig = make_keypair("original-message")
        assert verify_ed25519_signature(pub, "tampered-message", sig) is False

    def test_wrong_public_key_returns_false(self):
        _, sig = make_keypair("some-message")
        other_pub, _ = make_keypair("other-message")
        assert verify_ed25519_signature(other_pub, "some-message", sig) is False

    def test_invalid_hex_public_key_returns_false(self):
        _, sig = make_keypair("msg")
        assert verify_ed25519_signature("not-hex", "msg", sig) is False

    def test_invalid_hex_signature_returns_false(self):
        pub, _ = make_keypair("msg")
        assert verify_ed25519_signature(pub, "msg", "not-hex") is False

    def test_empty_message_is_valid(self):
        pub, sig = make_keypair("")
        assert verify_ed25519_signature(pub, "", sig) is True
