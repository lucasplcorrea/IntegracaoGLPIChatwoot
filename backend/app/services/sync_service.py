from __future__ import annotations

import logging

from httpx import HTTPStatusError

from app.repositories.history_repository import (
    get_or_create_contact,
    upsert_messages,
    upsert_snapshot,
)
from app.services.chatwoot_service import chatwoot_service

logger = logging.getLogger(__name__)


async def sync_contact_conversations(chatwoot_contact_id: int, inbox_id: int | None = None) -> int:
    """
    Fetches conversations for a contact from Chatwoot and persists them.
    Args: contact_id, optional inbox_id filter. Returns count of upserted conversations.
    """
    logger.info(f"Syncing conversations for contact {chatwoot_contact_id}")
    if inbox_id is not None:
        logger.info(f"  → Filtering by inbox_id: {inbox_id}")
    try:
        contact_raw = await chatwoot_service.fetch_contact(chatwoot_contact_id)
    except Exception as exc:
        logger.warning(f"Could not fetch contact {chatwoot_contact_id}: {exc}")
        contact_raw = {}

    contact = get_or_create_contact(
        chatwoot_contact_id=chatwoot_contact_id,
        name=contact_raw.get("name"),
        phone=contact_raw.get("phone_number"),
        email=contact_raw.get("email"),
        avatar_url=contact_raw.get("thumbnail"),
    )

    try:
        conversations_raw = await chatwoot_service.fetch_contact_conversations(chatwoot_contact_id)
    except HTTPStatusError as exc:
        if exc.response.status_code == 401:
            logger.error("Chatwoot returned 401 Unauthorized while fetching conversations. Check CHATWOOT_API_TOKEN and account_id.")
            return 0
        raise

    logger.info(f"Found {len(conversations_raw)} conversations for contact {chatwoot_contact_id}")

    count = 0
    for conv_raw in conversations_raw:
        conv_inbox_id = conv_raw.get("inbox_id")
        if inbox_id is not None and conv_inbox_id != inbox_id:
            logger.debug(f"Skipping conversation {conv_raw.get('id')} (inbox {conv_inbox_id} != {inbox_id})")
            continue

        try:
            conv_data = chatwoot_service.parse_conversation(conv_raw)
            messages_raw = await chatwoot_service.fetch_conversation_messages(conv_data["chatwoot_conversation_id"])
            messages = [chatwoot_service.parse_message(m) for m in messages_raw]

            # Build summary from last non-empty message
            summary = next(
                (m["content"] for m in reversed(messages) if m.get("content")),
                None,
            )

            snapshot = upsert_snapshot(
                contact_id=contact.id,
                data={**conv_data, "summary": summary},
            )
            upsert_messages(snapshot.id, messages)
            count += 1
        except Exception as exc:
            logger.error(f"Error syncing conversation {conv_raw.get('id')}: {exc}")

    return count


async def sync_single_conversation(chatwoot_conversation_id: int) -> None:
    """
    Syncs a single conversation (used on webhook trigger).
    """
    logger.info(f"Syncing single conversation {chatwoot_conversation_id}")
    try:
        conv_raw = await chatwoot_service.fetch_conversation(chatwoot_conversation_id)
    except Exception as exc:
        logger.error(f"Could not fetch conversation {chatwoot_conversation_id}: {exc}")
        return

    # Resolve contact
    meta = conv_raw.get("meta") or {}
    sender = meta.get("sender") or conv_raw.get("contact") or {}
    chatwoot_contact_id = sender.get("id")
    if not chatwoot_contact_id:
        logger.warning(f"No contact found in conversation {chatwoot_conversation_id}")
        return

    contact = get_or_create_contact(
        chatwoot_contact_id=chatwoot_contact_id,
        name=sender.get("name"),
        phone=sender.get("phone_number"),
        email=sender.get("email"),
        avatar_url=sender.get("thumbnail"),
    )

    conv_data = chatwoot_service.parse_conversation(conv_raw)
    try:
        messages_raw = await chatwoot_service.fetch_conversation_messages(chatwoot_conversation_id)
    except HTTPStatusError as exc:
        if exc.response.status_code == 401:
            logger.error("Chatwoot returned 401 Unauthorized while fetching messages. Check CHATWOOT_API_TOKEN and account_id.")
            return
        raise

    messages = [chatwoot_service.parse_message(m) for m in messages_raw]

    summary = next((m["content"] for m in reversed(messages) if m.get("content")), None)

    snapshot = upsert_snapshot(
        contact_id=contact.id,
        data={**conv_data, "summary": summary},
    )
    upsert_messages(snapshot.id, messages)
    logger.info(f"Synced conversation {chatwoot_conversation_id} → snapshot {snapshot.id}")
