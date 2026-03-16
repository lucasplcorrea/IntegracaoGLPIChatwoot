from fastapi import APIRouter, HTTPException, status

from app.repositories.history_repository import get_snapshot_by_conversation_id, get_snapshot_messages
from app.schemas.history import ConversationDetail, MessageItem

router = APIRouter(tags=["conversations"])


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationDetail)
async def get_conversation_messages(conversation_id: int) -> ConversationDetail:
    """Returns the locally-indexed messages for a given conversation."""
    snapshot = get_snapshot_by_conversation_id(conversation_id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not indexed yet. Trigger a sync first.",
        )
    messages = get_snapshot_messages(snapshot.id)
    return ConversationDetail(
        chatwoot_conversation_id=snapshot.chatwoot_conversation_id,
        status=snapshot.status,
        assignee_name=snapshot.assignee_name,
        summary=snapshot.summary,
        first_message_at=snapshot.first_message_at,
        last_message_at=snapshot.last_message_at,
        resolved_at=snapshot.resolved_at,
        messages=[
            MessageItem(
                chatwoot_message_id=m.chatwoot_message_id,
                message_type=m.message_type,
                content=m.content,
                sender_name=m.sender_name,
                sent_at=m.sent_at,
            )
            for m in messages
        ],
    )

from app.services.chatwoot_service import chatwoot_service

@router.get("/conversations/{conversation_id}/contact")
async def get_conversation_contact(conversation_id: int):
    """Fetches the conversation from Chatwoot API and returns its contact ID."""
    try:
        conv = await chatwoot_service.fetch_conversation(conversation_id)
        # Chatwoot API returns the sender under meta.sender.id usually
        meta = conv.get("meta", {})
        sender = meta.get("sender", {})
        contact_id = sender.get("id")
        if not contact_id:
            contact_id = conv.get("contact_inbox", {}).get("contact_id")
            
        if not contact_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not extract contact ID from the conversation data.",
            )
        return {"contact_id": contact_id}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
