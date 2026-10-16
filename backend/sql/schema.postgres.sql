-- AutoCare AI — tables used by User Story 2 (Ask a Diagnostic Question).
-- Table and column names follow the ER diagram exactly (unquoted, so Postgres
-- folds them to lower case: USERVEHICLE -> uservehicle, etc.).
-- The other ER tables (MaintenanceRecord, GraphNode, GraphEdge, ...) are owned
-- by the main schema and are not touched by this story.
--
-- Requires the pgvector extension for DocumentChunk.embedding.
-- Dimension 1024 matches BAAI/bge-m3; change it if the embedding model changes.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS vehicle (
    vehicle_id    TEXT PRIMARY KEY,
    manufacturer  TEXT NOT NULL,
    model         TEXT NOT NULL,
    variant       TEXT,
    year          INTEGER NOT NULL,
    engine        TEXT,
    transmission  TEXT,
    fuel_type     TEXT
);

CREATE TABLE IF NOT EXISTS uservehicle (
    user_vehicle_id    TEXT PRIMARY KEY,
    user_id            TEXT NOT NULL,
    vehicle_id         TEXT NOT NULL REFERENCES vehicle(vehicle_id),
    registration_year  INTEGER,
    current_mileage    INTEGER,
    last_reading_date  DATE,
    usage_profile      TEXT
);

-- DECISION (flagged in README): vehicle_id is NULLABLE here. The ER diagram
-- draws Document -> Vehicle as mandatory, but the generic OBD-II code
-- reference (SAE J2012) is not specific to one vehicle. NULL = "applies to
-- every vehicle". Without this, the DTC reference would have to be copied
-- once per Corolla model year.
CREATE TABLE IF NOT EXISTS document (
    document_id    TEXT PRIMARY KEY,
    vehicle_id     TEXT REFERENCES vehicle(vehicle_id),
    document_name  TEXT NOT NULL,
    document_type  TEXT NOT NULL,          -- owner_manual | dtc_reference | maintenance_schedule
    version        TEXT,
    source         TEXT,
    license_note   TEXT,
    ingest_date    DATE
);

CREATE TABLE IF NOT EXISTS documentchunk (
    chunk_id     TEXT PRIMARY KEY,
    document_id  TEXT NOT NULL REFERENCES document(document_id) ON DELETE CASCADE,
    section      TEXT,
    page_number  INTEGER,
    text         TEXT NOT NULL,
    embedding    vector(1024),
    chunk_type   TEXT                       -- narrative | warning | procedure | table | dtc_entry
);

CREATE TABLE IF NOT EXISTS diagnosticcode (
    code             TEXT PRIMARY KEY,
    description      TEXT NOT NULL,
    system           TEXT,
    possible_causes  TEXT,
    symptoms         TEXT,
    severity         TEXT,
    source_ref       TEXT
);

CREATE TABLE IF NOT EXISTS diagnosticcase (
    case_id             TEXT PRIMARY KEY,
    user_vehicle_id     TEXT REFERENCES uservehicle(user_vehicle_id),
    symptom_text        TEXT NOT NULL,
    language            TEXT,               -- en | ur | roman_ur
    code                TEXT REFERENCES diagnosticcode(code),
    predicted_category  TEXT,
    component_group     TEXT,
    predicted_urgency   TEXT,
    confidence          DOUBLE PRECISION,
    evidence_refs       TEXT,               -- JSON array of chunk_ids
    outcome             TEXT,
    provenance          TEXT                -- real | seeded
);

CREATE INDEX IF NOT EXISTS ix_document_vehicle      ON document(vehicle_id);
CREATE INDEX IF NOT EXISTS ix_documentchunk_doc     ON documentchunk(document_id);
CREATE INDEX IF NOT EXISTS ix_vehicle_scope         ON vehicle(lower(manufacturer), lower(model), year);
CREATE INDEX IF NOT EXISTS ix_diagnosticcase_uv     ON diagnosticcase(user_vehicle_id);

-- DECISION (flagged in README): sign-in and roles need a user table, which the ER
-- diagram does not have (uservehicle.user_id had no parent table). Roles: owner |
-- mechanic | admin.
CREATE TABLE IF NOT EXISTS appuser (
    user_id        TEXT PRIMARY KEY,
    full_name      TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    role           TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

-- ER: DamageImage (M10, Story 12). file_ref stays NULL: photos are not stored until the
-- consent process for keeping them exists (proposal §9). label_source = model:<method> for
-- predictions, team:<name> for human labels.
CREATE TABLE IF NOT EXISTS damageimage (
    image_id            TEXT PRIMARY KEY,
    case_id             TEXT REFERENCES diagnosticcase(case_id),
    vehicle_id          TEXT REFERENCES vehicle(vehicle_id),
    file_ref            TEXT,
    predicted_severity  TEXT,
    predicted_location  TEXT,
    model_confidence    REAL,
    label_source        TEXT,
    reviewed            BOOLEAN DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS ix_damageimage_case ON damageimage(case_id);
