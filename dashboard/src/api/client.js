const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  // 202 Accepted and other no-body responses
  if (res.status === 202 || res.headers.get("content-length") === "0") {
    return null;
  }
  return res.json();
}

/**
 * Returns the conversation history for a contact from the local index.
 * @param {number} contactId
 * @returns {Promise<Array>}
 */
export function getContactHistory(contactId) {
  return request(`/contacts/${contactId}/history`);
}

/**
 * Triggers an on-demand sync of all conversations for a contact.
 * @param {number} contactId
 * @returns {Promise<null>}
 */
export function syncContact(contactId) {
  return request(`/contacts/${contactId}/sync`, { method: "POST" });
}

/**
 * Returns the full messages for an indexed conversation.
 * @param {number} conversationId
 * @returns {Promise<object>}  ConversationDetail shape
 */
export function getConversationMessages(conversationId) {
  return request(`/conversations/${conversationId}/messages`);
}

/**
 * Returns all messages from all indexed conversations for a contact, chronologically.
 * @param {number} contactId
 * @returns {Promise<Array>} Array of MessageItem
 */
export function getContactMessages(contactId) {
  return request(`/contacts/${contactId}/messages`);
}
/**
 * Returns the contact ID and info for a conversation (fetches from Chatwoot API via backend).
 * @param {number} conversationId
 * @returns {Promise<object>} { contact_id: number }
 */
export function getConversationContact(conversationId) {
  return request(`/conversations/${conversationId}/contact`);
}
