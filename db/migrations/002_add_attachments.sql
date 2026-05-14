BEGIN;

-- Add attachments column to store media metadata
ALTER TABLE conversation_messages
ADD COLUMN IF NOT EXISTS attachments JSONB DEFAULT NULL;

-- Index for filtering messages with attachments
CREATE INDEX IF NOT EXISTS idx_messages_with_attachments
    ON conversation_messages (snapshot_id) WHERE attachments IS NOT NULL;

COMMIT;
