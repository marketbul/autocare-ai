-- AI Auto Pakistan: Data Engine Schema
-- Unified Relational Architecture supporting Multi-Source Automotive Intelligence

CREATE TABLE IF NOT EXISTS data_sources (
    source_id               TEXT PRIMARY KEY,
    name                    TEXT NOT NULL,
    source_type             TEXT NOT NULL,
    rights_basis            TEXT NOT NULL,
    is_automated            BOOLEAN NOT NULL,
    requires_api_key        BOOLEAN NOT NULL,
    attribution_required    BOOLEAN NOT NULL,
    rate_limit_policy       TEXT,
    enabled                 BOOLEAN DEFAULT TRUE,
    description             TEXT
);

CREATE TABLE IF NOT EXISTS vehicle_fleet (
    vehicle_id              TEXT PRIMARY KEY,
    make                    TEXT NOT NULL,
    model                   TEXT NOT NULL,
    variant                 TEXT,
    manufacturing_year      INTEGER,
    engine_cc               INTEGER,
    engine_type             TEXT,
    fuel_type               TEXT,
    transmission            TEXT,
    market_country          TEXT DEFAULT 'Pakistan'
);

CREATE TABLE IF NOT EXISTS fault_categories (
    category_id             TEXT PRIMARY KEY,
    name                    TEXT NOT NULL,
    name_ur                 TEXT NOT NULL,
    name_roman_ur           TEXT NOT NULL,
    description             TEXT,
    subcomponents_json      TEXT,
    symptom_keywords_json   TEXT,
    typical_causes_json     TEXT
);

CREATE TABLE IF NOT EXISTS media_assets (
    asset_id                TEXT PRIMARY KEY,
    asset_type              TEXT NOT NULL, -- audio | image | video
    relative_reference      TEXT NOT NULL,
    sha256_hash             TEXT NOT NULL,
    size_bytes              INTEGER,
    rights_basis            TEXT NOT NULL,
    attribution             TEXT,
    created_at              TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnostic_records (
    record_id               TEXT PRIMARY KEY,
    vehicle_id              TEXT REFERENCES vehicle_fleet(vehicle_id),
    fault_category_id       TEXT REFERENCES fault_categories(category_id),
    source_id               TEXT REFERENCES data_sources(source_id),
    problem_title           TEXT NOT NULL,
    problem_description     TEXT NOT NULL,
    symptoms_json           TEXT,
    suspected_causes_json   TEXT,
    confirmed_causes_json   TEXT,
    severity                TEXT,
    diagnosis_stage         TEXT NOT NULL,
    audio_asset_id          TEXT REFERENCES media_assets(asset_id),
    image_asset_id          TEXT REFERENCES media_assets(asset_id),
    video_asset_id          TEXT REFERENCES media_assets(asset_id),
    sound_category          TEXT,
    sound_description       TEXT,
    detected_component      TEXT,
    dashboard_warning_light TEXT,
    smoke_color             TEXT,
    recommended_solution    TEXT,
    repair_steps_json       TEXT,
    required_parts_json     TEXT,
    repair_success          BOOLEAN,
    verification_status     TEXT DEFAULT 'unverified',
    estimated_cost_pkr      REAL,
    parts_cost_pkr          REAL,
    labor_cost_pkr          REAL,
    city                    TEXT,
    price_date              TEXT,
    price_source            TEXT,
    source_url              TEXT,
    publication_date        TEXT,
    collection_date         TEXT NOT NULL,
    language                TEXT NOT NULL,
    rights_basis            TEXT NOT NULL,
    confidence_score        REAL DEFAULT 0.5,
    human_review_status     TEXT DEFAULT 'pending',
    reviewer_notes          TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp               TEXT NOT NULL,
    action                  TEXT NOT NULL,
    source_id               TEXT,
    record_id               TEXT,
    status                  TEXT NOT NULL,
    details_json            TEXT
);

CREATE INDEX IF NOT EXISTS ix_diag_vehicle ON diagnostic_records(vehicle_id);
CREATE INDEX IF NOT EXISTS ix_diag_category ON diagnostic_records(fault_category_id);
CREATE INDEX IF NOT EXISTS ix_diag_source ON diagnostic_records(source_id);
CREATE INDEX IF NOT EXISTS ix_diag_stage ON diagnostic_records(diagnosis_stage);
CREATE INDEX IF NOT EXISTS ix_fleet_make_model ON vehicle_fleet(lower(make), lower(model));
