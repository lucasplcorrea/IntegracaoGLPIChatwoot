from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from httpx import HTTPStatusError

from app.repositories.history_repository import get_contact_history, get_all_messages_for_contact
from app.schemas.history import ConversationItem, MessageItem
from app.services.sync_service import sync_contact_conversations

router = APIRouter(tags=["contacts"])


@router.get("/contacts/{contact_id}/history", response_model=list[ConversationItem])
async def get_history(contact_id: int) -> list[ConversationItem]:
    """Returns locally-indexed conversations for a contact, ordered by most recent first."""
    snapshots = get_contact_history(contact_id)
    return [
        ConversationItem(
            chatwoot_conversation_id=s.chatwoot_conversation_id,
            status=s.status,
            assignee_name=s.assignee_name,
            summary=s.summary,
            first_message_at=s.first_message_at,
            last_message_at=s.last_message_at,
            resolved_at=s.resolved_at,
        )
        for s in snapshots
    ]

@router.get("/contacts/{contact_id}/messages", response_model=list[MessageItem])
async def get_contact_messages(contact_id: int) -> list[MessageItem]:
    """Returns all locally-indexed messages for a contact, ordered chronologically."""
    messages = get_all_messages_for_contact(contact_id)
    return [
        MessageItem(
            chatwoot_message_id=m.chatwoot_message_id,
            message_type=m.message_type,
            content=m.content,
            sender_name=m.sender_name,
            sent_at=m.sent_at,
        )
        for m in messages
    ]

@router.post("/contacts/{contact_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_contact(contact_id: int, background_tasks: BackgroundTasks) -> dict:
    """Triggers an on-demand sync of all conversations for a contact from Chatwoot."""
    background_tasks.add_task(sync_contact_conversations, contact_id)
    return {"status": "sync_started", "contact_id": contact_id}
