import { StatusBadge } from "./StatusBadge.jsx";

function formatDate(isoString) {
  if (!isoString) return "–";
  const d = new Date(isoString);
  return d.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ConversationList({ conversations, activeId, onSelect, currentConversationId }) {
  if (!conversations || conversations.length === 0) {
    return (
      <div className="section">
        <div className="section-header">
          <span className="section-title">Histórico do Cliente</span>
          <span className="section-count">0</span>
        </div>
        <div className="conv-list-empty">Nenhuma conversa indexada ainda.</div>
      </div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <span className="section-title">Histórico do Cliente</span>
        <span className="section-count">{conversations.length}</span>
      </div>
      <ul className="conv-list">
        {conversations.map((conv) => {
          const isActive = conv.chatwoot_conversation_id === activeId;
          const isCurrent = conv.chatwoot_conversation_id === currentConversationId;
          return (
            <li
              key={conv.chatwoot_conversation_id}
              className={`conv-item${isActive ? " active" : ""}`}
              onClick={() => onSelect(conv)}
            >
              <div className="conv-item-header">
                <span className="conv-id">
                  #{conv.chatwoot_conversation_id}
                  {isCurrent && (
                    <span style={{ marginLeft: 5, fontSize: 9, color: "var(--accent-light)", background: "var(--accent-dim)", padding: "1px 5px", borderRadius: 20 }}>
                      atual
                    </span>
                  )}
                </span>
                <span className="conv-date">
                  {formatDate(conv.last_message_at || conv.resolved_at)}
                </span>
              </div>

              {conv.summary && (
                <div className="conv-summary">{conv.summary}</div>
              )}

              <div className="conv-footer">
                <span className="conv-agent">
                  {conv.assignee_name ? `👤 ${conv.assignee_name}` : "Sem agente"}
                </span>
                <StatusBadge status={conv.status} />
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
