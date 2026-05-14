from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AttachmentItem(BaseModel):
    filename: str
    file_type: str
    url: str

    model_config = {"from_attributes": True}


class MessageItem(BaseModel):
    chatwoot_message_id: int
    message_type: str | None
    content: str | None
    sender_name: str | None
    sent_at: datetime | None
    attachments: list[AttachmentItem] | None = None

    model_config = {"from_attributes": True}


class ConversationItem(BaseModel):
    chatwoot_conversation_id: int
    inbox_id: int | None = None
    status: str
    assignee_name: str | None
    summary: str | None
    first_message_at: datetime | None
    last_message_at: datetime | None
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationItem):
    messages: list[MessageItem] = []
