import { StatusBadge } from "./StatusBadge.jsx";

function formatTime(isoString) {
  if (!isoString) return "";
  const d = new Date(isoString);
  return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

export function formatDateFull(isoString) {
  if (!isoString) return "–";
  const d = new Date(isoString);
  return d.toLocaleDateString("pt-BR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export function MessageBubble({ message }) {
  const direction = message.message_type === "outgoing" ? "outgoing"
    : message.message_type === "activity" ? "activity"
    : "incoming";

  return (
    <div className={`message-row ${direction}`}>
      <div className="message-bubble">
        {direction !== "activity" && message.sender_name && (
          <div className="msg-sender">{message.sender_name}</div>
        )}
        <div className="msg-content">{message.content || <em style={{ opacity: 0.5 }}>[sem texto]</em>}</div>
        {message.sent_at && (
          <div className="msg-time">{formatDateFull(message.sent_at).slice(0, 5)} {formatTime(message.sent_at)}</div>
        )}
      </div>
    </div>
  );
}

export function ConversationDetail({ detail, onBack, loading }) {
  return (
    <div className="section">
      <div className="conv-detail-back" onClick={onBack}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        Voltar ao histórico
      </div>

      {loading ? (
        <div className="loading-msg">Carregando mensagens…</div>
      ) : !detail ? (
        <div className="loading-msg">Nenhum dado disponível.</div>
      ) : (
        <>
          <div className="section-header" style={{ borderTop: "none" }}>
            <span className="section-title">Conversa #{detail.chatwoot_conversation_id}</span>
            <StatusBadge status={detail.status} />
          </div>

          <div style={{ padding: "6px 12px", display: "flex", gap: 12, flexWrap: "wrap", borderBottom: "1px solid var(--border)" }}>
            {detail.assignee_name && (
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>👤 {detail.assignee_name}</span>
            )}
            {detail.resolved_at && (
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>✅ {formatDateFull(detail.resolved_at)}</span>
            )}
            {detail.last_message_at && (
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>🕐 {formatDateFull(detail.last_message_at)}</span>
            )}
          </div>

          <div className="messages-list">
            {detail.messages && detail.messages.length > 0 ? (
              detail.messages.map((m, i) => (
                <MessageBubble key={m.chatwoot_message_id ?? i} message={m} />
              ))
            ) : (
              <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 12, padding: 16 }}>
                Nenhuma mensagem indexada.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
