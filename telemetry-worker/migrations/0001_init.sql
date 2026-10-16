-- Teyvat Spire run telemetry, schema v1.
-- One row per accepted run. No IP address, Steam id, net id or name is ever
-- written to this database: install_id is a random UUID the mod generates.
CREATE TABLE runs (
  id             TEXT PRIMARY KEY,      -- client run_uuid; a repeat is a no-op
  received_at    INTEGER NOT NULL,      -- unix seconds, server clock
  install_id     TEXT NOT NULL,
  schema_version INTEGER NOT NULL,
  mod_version    TEXT NOT NULL,
  variant        TEXT NOT NULL,         -- beta | public
  character      TEXT NOT NULL,
  ascension      INTEGER NOT NULL,
  victory        INTEGER NOT NULL,      -- 0 | 1
  floor_reached  INTEGER NOT NULL,
  payload        TEXT NOT NULL          -- the validated record, as JSON
);

CREATE INDEX runs_install_time ON runs (install_id, received_at);
CREATE INDEX runs_received ON runs (received_at);
CREATE INDEX runs_character ON runs (character, variant);
