import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    chatwoot_contact_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    snapshots: Mapped[list["ConversationSnapshot"]] = relationship(
        "ConversationSnapshot", back_populates="contact", cascade="all, delete-orphan"
    )


class ConversationSnapshot(Base):
    __tablename__ = "conversation_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    chatwoot_conversation_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    inbox_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    assignee_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="resolved")
    # Preview of the last message content
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    contact: Mapped["Contact"] = relationship("Contact", back_populates="snapshots")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="snapshot", cascade="all, delete-orphan", order_by="ConversationMessage.sent_at"
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    snapshot_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("conversation_snapshots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chatwoot_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # "incoming" | "outgoing" | "activity"
    message_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    snapshot: Mapped["ConversationSnapshot"] = relationship("ConversationSnapshot", back_populates="messages")

    __table_args__ = (
        __import__("sqlalchemy").UniqueConstraint("snapshot_id", "chatwoot_message_id", name="uq_snapshot_message"),
    )
