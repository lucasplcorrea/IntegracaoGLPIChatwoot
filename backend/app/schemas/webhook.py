from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


# ── Webhook payload ─────────────────────────────────────────────────────────

class WebhookConversation(BaseModel):
    id: int
    status: str | None = None

    model_config = {"extra": "allow"}


class WebhookContact(BaseModel):
    id: int
    name: str | None = None

    model_config = {"extra": "allow"}


class ChatwootWebhookEvent(BaseModel):
    event: str
    conversation: WebhookConversation | None = None
    contact: WebhookContact | None = None

    model_config = {"extra": "allow"}
