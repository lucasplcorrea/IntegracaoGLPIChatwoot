from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_MESSAGE_TYPE_MAP = {0: "incoming", 1: "outgoing", 2: "activity", 3: "template"}


def _parse_ts(value: int | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


class ChatwootService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.chatwoot_base_url,
            headers={"api_access_token": settings.chatwoot_api_token},
            timeout=30,
            follow_redirects=True,
        )

    def _account_url(self, path: str) -> str:
        return f"/api/v1/accounts/{settings.chatwoot_account_id}{path}"

    async def fetch_contact(self, contact_id: int) -> dict:
        resp = await self._client.get(self._account_url(f"/contacts/{contact_id}"))
        resp.raise_for_status()
        return resp.json()

    async def fetch_contact_conversations(self, contact_id: int) -> list[dict]:
        resp = await self._client.get(self._account_url(f"/contacts/{contact_id}/conversations"))
        resp.raise_for_status()
        data = resp.json()
        # The API returns {"data": {"meta": {...}, "payload": [...]}}
        if isinstance(data, dict):
            payload = data.get("payload") or data.get("data", {})
            if isinstance(payload, dict):
                payload = payload.get("payload", [])
            return payload if isinstance(payload, list) else []
        return []

    async def fetch_conversation(self, conversation_id: int) -> dict:
        resp = await self._client.get(self._account_url(f"/conversations/{conversation_id}"))
        resp.raise_for_status()
        return resp.json()

    async def fetch_conversation_messages(self, conversation_id: int) -> list[dict]:
        all_messages = []
        before_id = None
        while True:
            params = {}
            if before_id:
                params["before"] = before_id
                
            resp = await self._client.get(
                self._account_url(f"/conversations/{conversation_id}/messages"),
                params=params
            )
            resp.raise_for_status()
            data = resp.json()
            payload = data.get("payload", []) if isinstance(data, dict) else []
            
            if not payload:
                break
                
            # As mensagens retornadas pela API no modo 'before' paginam do mais recente para o mais antigo,
            # porém cada lote é ordenado cronologicamente internamente.
            all_messages = payload + all_messages
            
            # O limite padrao do Chatwoot é 20, se vier menos, chegamos no topo.
            if len(payload) < 20:
                break
                
            # Pega o ID da mensagem mais antiga (a primeira do array do lote) para pedir a página anterior
            before_id = payload[0].get("id")
            if not before_id:
                break
                
        return all_messages

    def parse_message(self, raw: dict) -> dict:
        """Normalizes a raw Chatwoot message dict into a flat dict."""
        msg_type_int = raw.get("message_type", 0)
        msg_type = _MESSAGE_TYPE_MAP.get(msg_type_int, str(msg_type_int))
        sender = raw.get("sender") or {}
        
        content = raw.get("content") or ""
        
        attachments = raw.get("attachments") or []
        for att in attachments:
            url = att.get("data_url")
            if url:
                file_type = att.get("file_type", "arquivo")
                # Append basic attachment text
                content += f"\n\n📎 Anexo ({file_type}): {url}"
                
        return {
            "chatwoot_message_id": raw.get("id"),
            "message_type": msg_type,
            "content": content.strip() or None,
            "sender_name": sender.get("name"),
            "sent_at": _parse_ts(raw.get("created_at")),
        }

    def parse_conversation(self, raw: dict) -> dict:
        """Normalizes a raw Chatwoot conversation dict into a flat dict."""
        meta = raw.get("meta") or {}
        assignee = raw.get("assignee") or meta.get("assignee") or {}
        return {
            "chatwoot_conversation_id": raw.get("id"),
            "inbox_id": raw.get("inbox_id"),
            "assignee_name": assignee.get("name"),
            "status": raw.get("status", ""),
            "first_message_at": _parse_ts(meta.get("created_at") or raw.get("created_at")),
            "last_message_at": _parse_ts(meta.get("last_activity_at") or raw.get("updated_at")),
            "resolved_at": _parse_ts(raw.get("updated_at") if raw.get("status") == "resolved" else None),
        }


chatwoot_service = ChatwootService()
