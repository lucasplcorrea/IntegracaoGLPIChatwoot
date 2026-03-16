import { useEffect, useState } from "react";
import { getContactHistory, getContactMessages, syncContact, getConversationContact } from "../api/client.js";
import { useChatwootContext } from "../hooks/useChatwootContext.js";
import { ContactHeader } from "../components/ContactHeader.jsx";
import { MessageBubble } from "../components/ConversationDetail.jsx";

export default function HistoryPage() {
  const {
    contactId,
    conversationId,
    contactProfile,
  } = useChatwootContext();

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  
  const [unifiedMessages, setUnifiedMessages] = useState(null);
  const [resolvedContactId, setResolvedContactId] = useState(null);



  // Resolve contact ID: if we only have conversationId, we fetch it from backend
  useEffect(() => {
    if (contactId) {
      setResolvedContactId(contactId);
      return;
    }
    if (conversationId && !contactId) {
      getConversationContact(conversationId)
        .then(data => {
          if (data.contact_id) setResolvedContactId(data.contact_id);
        })
        .catch(err => console.error("Could not resolve contact from conversation", err));
    }
  }, [contactId, conversationId]);

  // Load unified messages and history whenever resolvedContactId resolves
  useEffect(() => {
    if (!resolvedContactId) return;
    setError(null);
    setLoading(true);
    setUnifiedMessages(null);

    getContactHistory(resolvedContactId)
      .then(setHistory)
      .catch(console.error);

    getContactMessages(resolvedContactId)
      .then(setUnifiedMessages)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [resolvedContactId]);

  async function handleSync() {
    if (!resolvedContactId || syncing) return;
    setSyncing(true);
    setError(null);
    try {
      await syncContact(resolvedContactId);
      // Wait a bit then reload history
      await new Promise((r) => setTimeout(r, 1500));
      
      const newHistory = await getContactHistory(resolvedContactId);
      setHistory(newHistory);
      
      const updatedMessages = await getContactMessages(resolvedContactId);
      setUnifiedMessages(updatedMessages);
    } catch (err) {
      setError(err.message);
    } finally {
      setSyncing(false);
    }
  }



  return (
    <div className="app">
      <header className="app-header">
        <h1>Histórico do Cliente</h1>
        <p className="subtitle">Conversas indexadas via Chatwoot</p>
      </header>

      <div className="app-body">
        {error && <div className="error-msg">⚠ {error}</div>}

        {resolvedContactId ? (
          <>
            <ContactHeader contactId={resolvedContactId} history={history} profile={contactProfile} />

            <div className="section" style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
              <div className="section-header">
                <span className="section-title">Feed Histórico Contínuo</span>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <span className="section-count">{unifiedMessages?.length ?? 0}</span>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={handleSync}
                    disabled={syncing || loading}
                  >
                    {syncing ? "Sincronizando…" : "↻ Sync"}
                  </button>
                </div>
              </div>
              
              {loading ? (
                <div className="loading-msg">Carregando feed de mensagens...</div>
              ) : (
                <div className="messages-list" style={{ flex: 1, overflowY: "auto", padding: "12px" }}>
                  {unifiedMessages && unifiedMessages.length > 0 ? (
                    unifiedMessages.map((m, i) => (
                      <MessageBubble key={m.chatwoot_message_id ?? i} message={m} />
                    ))
                  ) : (
                    <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 12, padding: 16 }}>
                      Nenhuma mensagem indexada. Clique em Sync para buscar.
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="no-contact-msg">
            <h2>Contato não identificado</h2>
            <p>
              Abra uma conversa no Chatwoot para o painel carregar automaticamente.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
