from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.models import Contact, ConversationMessage, ConversationSnapshot

logger = logging.getLogger(__name__)


def get_or_create_contact(
    chatwoot_contact_id: int,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    avatar_url: str | None = None,
) -> Contact:
    session = SessionLocal()
    try:
        contact = session.query(Contact).filter_by(chatwoot_contact_id=chatwoot_contact_id).one_or_none()
        if contact is None:
            contact = Contact(
                chatwoot_contact_id=chatwoot_contact_id,
                name=name,
                phone=phone,
                email=email,
                avatar_url=avatar_url,
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)
        else:
            changed = False
            if name and contact.name != name:
                contact.name = name
                changed = True
            if phone and contact.phone != phone:
                contact.phone = phone
                changed = True
            if email and contact.email != email:
                contact.email = email
                changed = True
            if avatar_url and contact.avatar_url != avatar_url:
                contact.avatar_url = avatar_url
                changed = True
            if changed:
                contact.updated_at = datetime.now(timezone.utc)
                session.commit()
        return contact
    finally:
        session.close()


def upsert_snapshot(contact_id: str, data: dict) -> ConversationSnapshot:
    session = SessionLocal()
    try:
        conv_id = data["chatwoot_conversation_id"]
        snapshot = session.query(ConversationSnapshot).filter_by(chatwoot_conversation_id=conv_id).one_or_none()
        if snapshot is None:
            snapshot = ConversationSnapshot(
                chatwoot_conversation_id=conv_id,
                contact_id=contact_id,
                inbox_id=data.get("inbox_id"),
                assignee_name=data.get("assignee_name"),
                status=data.get("status", ""),
                summary=data.get("summary"),
                first_message_at=data.get("first_message_at"),
                last_message_at=data.get("last_message_at"),
                resolved_at=data.get("resolved_at"),
            )
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
        else:
            snapshot.assignee_name = data.get("assignee_name", snapshot.assignee_name)
            snapshot.status = data.get("status", snapshot.status)
            snapshot.summary = data.get("summary") or snapshot.summary
            snapshot.first_message_at = data.get("first_message_at") or snapshot.first_message_at
            snapshot.last_message_at = data.get("last_message_at") or snapshot.last_message_at
            snapshot.resolved_at = data.get("resolved_at") or snapshot.resolved_at
            session.commit()
        return snapshot
    finally:
        session.close()


def upsert_messages(snapshot_id: str, messages: list[dict]) -> None:
    if not messages:
        return
    session = SessionLocal()
    try:
        for msg in messages:
            try:
                existing = (
                    session.query(ConversationMessage)
                    .filter_by(snapshot_id=snapshot_id, chatwoot_message_id=msg["chatwoot_message_id"])
                    .one_or_none()
                )
                if existing is None:
                    session.add(
                        ConversationMessage(
                            snapshot_id=snapshot_id,
                            chatwoot_message_id=msg["chatwoot_message_id"],
                            message_type=msg.get("message_type"),
                            content=msg.get("content"),
                            sender_name=msg.get("sender_name"),
                            sent_at=msg.get("sent_at"),
                        )
                    )
            except IntegrityError:
                session.rollback()
        session.commit()
    finally:
        session.close()


def get_contact_history(chatwoot_contact_id: int) -> list[ConversationSnapshot]:
    session = SessionLocal()
    try:
        contact = session.query(Contact).filter_by(chatwoot_contact_id=chatwoot_contact_id).one_or_none()
        if not contact:
            return []
        return (
            session.query(ConversationSnapshot)
            .filter_by(contact_id=contact.id)
            .order_by(ConversationSnapshot.last_message_at.desc().nulls_last())
            .all()
        )
    finally:
        session.close()


def get_snapshot_by_conversation_id(chatwoot_conversation_id: int) -> ConversationSnapshot | None:
    session = SessionLocal()
    try:
        return session.query(ConversationSnapshot).filter_by(chatwoot_conversation_id=chatwoot_conversation_id).one_or_none()
    finally:
        session.close()


def get_snapshot_messages(snapshot_id: str) -> list[ConversationMessage]:
    session = SessionLocal()
    try:
        return (
            session.query(ConversationMessage)
            .filter_by(snapshot_id=snapshot_id)
            .order_by(ConversationMessage.sent_at.asc().nulls_last())
            .all()
        )
    finally:
        session.close()


def get_all_messages_for_contact(chatwoot_contact_id: int) -> list[ConversationMessage]:
    """Retrieves all messages across all snapshots for a given contact, ordered chronologically."""
    session = SessionLocal()
    try:
        contact = session.query(Contact).filter_by(chatwoot_contact_id=chatwoot_contact_id).one_or_none()
        if not contact:
            return []
            
        snapshot_ids = [s.id for s in session.query(ConversationSnapshot.id).filter_by(contact_id=contact.id).all()]
        if not snapshot_ids:
            return []
            
        return (
            session.query(ConversationMessage)
            .filter(ConversationMessage.snapshot_id.in_(snapshot_ids))
            .order_by(ConversationMessage.sent_at.asc().nulls_last())
            .all()
        )
    finally:
        session.close()
