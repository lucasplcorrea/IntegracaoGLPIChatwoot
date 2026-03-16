import hashlib
import hmac


def verify_chatwoot_signature(payload_bytes: bytes, signature_header: str | None, secret: str) -> bool:
    """Validates the HMAC-SHA256 signature sent by Chatwoot on webhook requests."""
    if not secret:
        # If no secret is configured, skip validation (useful for development)
        return True
    if not signature_header:
        return False
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    # Chatwoot sends the signature as plain hex (no "sha256=" prefix)
    return hmac.compare_digest(expected, signature_header.strip())
