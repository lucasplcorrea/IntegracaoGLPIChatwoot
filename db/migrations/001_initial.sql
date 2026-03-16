BEGIN;

CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chatwoot_contact_id BIGINT NOT NULL UNIQUE,
    name TEXT,
    phone TEXT,
    email TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chatwoot_conversation_id BIGINT NOT NULL UNIQUE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    inbox_id BIGINT,
    assignee_name TEXT,
    status TEXT NOT NULL DEFAULT 'resolved',
    summary TEXT,
    first_message_at TIMESTAMPTZ,
    last_message_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES conversation_snapshots(id) ON DELETE CASCADE,
    chatwoot_message_id BIGINT NOT NULL,
    message_type TEXT,
    content TEXT,
    sender_name TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_snapshot_message UNIQUE (snapshot_id, chatwoot_message_id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_snapshots_contact_last
    ON conversation_snapshots (contact_id, last_message_at DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_messages_snapshot_sent
    ON conversation_messages (snapshot_id, sent_at ASC NULLS LAST);

COMMIT;
