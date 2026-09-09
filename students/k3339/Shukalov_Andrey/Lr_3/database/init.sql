CREATE TABLE IF NOT EXISTS parsed_pages (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    approach VARCHAR(32) NOT NULL
        CHECK (approach IN ('threading', 'multiprocessing', 'asyncio')),
    parsed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_parsed_pages_approach
ON parsed_pages (approach);