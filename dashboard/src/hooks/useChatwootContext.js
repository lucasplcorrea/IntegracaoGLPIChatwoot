import { useEffect, useMemo, useState } from "react";

/**
 * Extracts contact_id and conversation_id from the current URL, the parent
 * frame URL (Chatwoot embeds the Dashboard App in an iframe), and localStorage
 * as a manual fallback.
 */
function parseChatwootContext() {
  const candidates = [];

  // Own URL
  candidates.push(window.location.href);

  // Parent frame URL (may throw cross-origin)
  try {
    if (window.parent && window.parent !== window) {
      candidates.push(window.parent.location.href);
    }
  } catch (_) {}

  // document.referrer
  if (document.referrer) candidates.push(document.referrer);

  let contactId = null;
  let conversationId = null;

  const CONVERSATION_RE = /\/conversations\/(\d+)/i;
  const CONTACT_RE = /\/contacts\/(\d+)/i;

  for (const url of candidates) {
    try {
      const u = new URL(url, window.location.origin);
      const q = u.searchParams;

      if (!contactId) {
        const fromQuery = q.get("contact_id") || q.get("contactId");
        const fromPath = u.pathname.match(CONTACT_RE)?.[1];
        contactId = fromQuery ? Number(fromQuery) : fromPath ? Number(fromPath) : null;
      }

      if (!conversationId) {
        const fromQuery = q.get("conversation_id") || q.get("conversationId");
        const fromPath = u.pathname.match(CONVERSATION_RE)?.[1];
        conversationId = fromQuery ? Number(fromQuery) : fromPath ? Number(fromPath) : null;
      }

      if (contactId && conversationId) break;
    } catch (_) {}
  }

  return { contactId, conversationId };
}

/**
 * Returns the Chatwoot context (contactId, conversationId) detected from the
 * embedding URL. Also provides manual override helpers persisted in localStorage.
 */
export function useChatwootContext() {
  const detected = useMemo(parseChatwootContext, []);

  const [appContextContact, setAppContextContact] = useState(null);
  const [appContextConversation, setAppContextConversation] = useState(null);

  useEffect(() => {
    // Clear any residual manual values from local storage just in case
    localStorage.removeItem("chatwoot.manualContactId");
    localStorage.removeItem("chatwoot.manualConversationId");

    const handleMessage = (event) => {
      try {
        const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        if (data && data.event === "appContext" && data.data) {
          if (data.data.contact) {
            setAppContextContact(data.data.contact);
          }
          if (data.data.conversation) {
            setAppContextConversation(data.data.conversation);
          }
        }
      } catch (e) {
        // ignore parse errors
      }
    };
    window.addEventListener("message", handleMessage);

    // Tentar forçar o Chatwoot a reenviar o contexto atual
    // útil para SPAs e iframes que demoraram a carregar o DOM.
    if (window.parent && window.parent !== window) {
      window.parent.postMessage('chatwoot-dashboard-app:fetch-info', '*');
      
      // Polling leve para garantir nos primeiros segundos
      const interval = setInterval(() => {
        if (!appContextContact) {
          window.parent.postMessage('chatwoot-dashboard-app:fetch-info', '*');
        }
      }, 2000);
      
      return () => {
        window.removeEventListener("message", handleMessage);
        clearInterval(interval);
      };
    }

    return () => window.removeEventListener("message", handleMessage);
  }, [appContextContact]);

  const contactId = appContextContact?.id || detected.contactId;
  const conversationId = appContextConversation?.id || detected.conversationId;

  return {
    contactId,
    conversationId,
    contactProfile: appContextContact,
    detected,
  };
}
