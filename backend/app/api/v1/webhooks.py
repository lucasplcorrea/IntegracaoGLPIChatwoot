from fastapi import APIRouter, Header, HTTPException, Request, status
from httpx import HTTPStatusError

from app.core.config import settings
from app.core.security import verify_chatwoot_signature
from app.schemas.webhook import ChatwootWebhookEvent
from app.services.sync_service import sync_single_conversation

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/chatwoot", status_code=status.HTTP_202_ACCEPTED)
async def receive_chatwoot_webhook(
    request: Request,
    x_chatwoot_signature: str | None = Header(default=None),
) -> dict[str, str]:
    payload_bytes = await request.body()

    if not verify_chatwoot_signature(payload_bytes, x_chatwoot_signature, settings.chatwoot_webhook_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    payload_json = await request.json()
    event = ChatwootWebhookEvent.model_validate(payload_json)

    # Sync conversation whenever a status change happens (resolved, open, etc.)
    if event.event == "conversation_status_changed" and event.conversation:
        try:
            await sync_single_conversation(event.conversation.id)
        except HTTPStatusError as exc:
            # Don't fail the webhook — log and return accepted
            import logging
            logging.getLogger(__name__).error(f"Sync error for conversation {event.conversation.id}: {exc}")

    return {"status": "accepted"}
