-- SQLite mirror of schema.postgres.sql, used for local development and tests.
-- Only difference: DocumentChunk.embedding is stored as JSON text.

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

CREATE TABLE IF NOT EXISTS document (
    document_id    TEXT PRIMARY KEY,
    vehicle_id     TEXT REFERENCES vehicle(vehicle_id),
    document_name  TEXT NOT NULL,
    document_type  TEXT NOT NULL,
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
    embedding    TEXT,
    chunk_type   TEXT
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
    language            TEXT,
    code                TEXT REFERENCES diagnosticcode(code),
    predicted_category  TEXT,
    component_group     TEXT,
    predicted_urgency   TEXT,
    confidence          REAL,
    evidence_refs       TEXT,
    outcome             TEXT,
    provenance          TEXT
);

CREATE INDEX IF NOT EXISTS ix_document_vehicle  ON document(vehicle_id);
CREATE INDEX IF NOT EXISTS ix_documentchunk_doc ON documentchunk(document_id);

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
    reviewed            INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_damageimage_case ON damageimage(case_id);
