"""Formal 4-Tier Data Lakehouse Schemas for AutoCare AI.

Defines the exact structure, data types, and transformation pipelines across:
1. Bronze Tier: Raw CAN-bus OBD-II JSON messages with SHA-256 CAS deduplication.
2. Silver Tier: Columnar Snappy Parquet schema with hierarchical partition layout.
3. Gold Tier: Relational application models (SQLite / PostgreSQL).
4. Fast Cache Tier: 65,536-bit Counting Bloom Filter in RAM.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# 1. BRONZE TIER SCHEMA (RAW TELEMETRY LANDING ZONE)
# ---------------------------------------------------------------------------

class BronzeTelemetryEvent(BaseModel):
    """Raw CAN-bus OBD-II sensor event received at the MinIO S3 landing zone."""
    timestamp: str = Field(..., description="ISO 8601 timestamp (e.g. 2026-11-17T08:30:00.125Z)")
    vin: str = Field(..., min_length=11, max_length=17, description="Vehicle Identification Number")
    make: str = Field(..., description="Vehicle Manufacturer (e.g. Toyota, Honda, Suzuki)")
    model: str = Field(..., description="Model Name (e.g. Corolla, Civic, Swift)")
    year: int = Field(..., ge=1990, le=2030, description="Model Manufacturing Year")
    region: str = Field(default="Punjab", description="Operating geographic region in Pakistan")
    engine_rpm: int = Field(..., ge=0, le=9000, description="Engine speed in RPM")
    speed_kmh: float = Field(..., ge=0.0, le=300.0, description="Vehicle road speed in km/h")
    coolant_temp_c: float = Field(..., ge=-40.0, le=150.0, description="Engine coolant temperature in Celsius")
    fuel_trim_pct: float = Field(..., ge=-50.0, le=50.0, description="Short-term fuel trim percentage")
    maf_rate_gs: float = Field(..., ge=0.0, le=500.0, description="Mass Air Flow in grams/second")
    throttle_pos_pct: float = Field(default=0.0, ge=0.0, le=100.0, description="Throttle position percentage")
    active_dtc_codes: List[str] = Field(default_factory=list, description="Active OBD-II fault codes (e.g. P0217)")
    sha256_cas_hash: Optional[str] = Field(default=None, description="SHA-256 Content-Addressable Storage hash")

    def compute_cas_hash(self) -> str:
        """Compute SHA-256 digest over normalized payload for zero-duplicate storage."""
        payload = f"{self.vin}_{self.timestamp}_{self.engine_rpm}_{self.speed_kmh}_{self.coolant_temp_c}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

# ---------------------------------------------------------------------------
# 2. SILVER TIER SCHEMA (COLUMNAR SNAPPY PARQUET LAKEHOUSE)
# ---------------------------------------------------------------------------

SILVER_PARQUET_SCHEMA_DEF = {
    "table_name": "silver_telemetry_lakehouse",
    "compression": "snappy",
    "partition_keys": ["make", "model", "year", "region"],
    "directory_format": "/lakehouse/telemetry/make={make}/model={model}/year={year}/region={region}/part-{uuid}.snappy.parquet",
    "target_block_size_mb": 128,
    "columns": [
        {"name": "timestamp_epoch_ms", "type": "int64", "nullable": False, "doc": "Unix epoch milliseconds"},
        {"name": "vin_token", "type": "string", "nullable": False, "doc": "Hashed pseudonymized VIN"},
        {"name": "engine_rpm", "type": "int32", "nullable": False},
        {"name": "speed_kmh", "type": "float32", "nullable": False},
        {"name": "coolant_temp_c", "type": "float32", "nullable": False},
        {"name": "fuel_trim_pct", "type": "float32", "nullable": False},
        {"name": "maf_rate_gs", "type": "float32", "nullable": False},
        {"name": "throttle_pos_pct", "type": "float32", "nullable": False},
        {"name": "dtc_count", "type": "int16", "nullable": False},
        {"name": "primary_dtc", "type": "string", "nullable": True},
        {"name": "anomaly_score", "type": "float32", "nullable": True}
    ]
}

# ---------------------------------------------------------------------------
# 3. GOLD TIER SCHEMAS (RELATIONAL APPLICATION DATABASE)
# ---------------------------------------------------------------------------

GOLD_RELATIONAL_SCHEMAS = {
    "vehicles": {
        "columns": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "vin": "VARCHAR(17) UNIQUE NOT NULL",
            "make": "VARCHAR(50) NOT NULL",
            "model": "VARCHAR(50) NOT NULL",
            "year": "INTEGER NOT NULL",
            "engine_type": "VARCHAR(30)",
            "odometer_km": "INTEGER DEFAULT 0",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
    },
    "diagnostic_sessions": {
        "columns": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "vehicle_id": "INTEGER REFERENCES vehicles(id)",
            "user_query": "TEXT NOT NULL",
            "detected_dtc": "VARCHAR(10)",
            "safety_tier": "VARCHAR(20) NOT NULL",  # DANGER, MAJOR, MODERATE, MINOR
            "ai_citation": "TEXT",
            "confidence_score": "REAL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
    },
    "manual_chunks": {
        "columns": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "vehicle_model": "VARCHAR(50) NOT NULL",
            "chapter": "VARCHAR(100)",
            "section": "VARCHAR(100)",
            "page_number": "INTEGER NOT NULL",
            "content_text": "TEXT NOT NULL",
            "embedding_vector": "BLOB"
        }
    },
    "mechanic_workshops": {
        "columns": {
            "id": "VARCHAR(30) PRIMARY KEY",
            "workshop_name": "VARCHAR(150) NOT NULL",
            "specialty_code": "VARCHAR(50) NOT NULL",
            "city": "VARCHAR(50) NOT NULL",
            "latitude": "REAL NOT NULL",
            "longitude": "REAL NOT NULL",
            "rating_stars": "REAL DEFAULT 4.5",
            "active_queue_slots": "INTEGER DEFAULT 2"
        }
    },
    "dispatch_tickets": {
        "columns": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "session_id": "INTEGER REFERENCES diagnostic_sessions(id)",
            "workshop_id": "VARCHAR(30) REFERENCES mechanic_workshops(id)",
            "fault_subsystem": "VARCHAR(50) NOT NULL",
            "estimated_pkr_low": "INTEGER",
            "estimated_pkr_high": "INTEGER",
            "dispatch_status": "VARCHAR(30) DEFAULT 'DISPATCHED'",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
    }
}

# ---------------------------------------------------------------------------
# 4. FAST CACHE TIER (COUNTING BLOOM FILTER)
# ---------------------------------------------------------------------------

class CountingBloomFilter:
    """Memory-efficient Counting Bloom Filter for O(1) diagnostic trouble code set membership."""
    def __init__(self, size: int = 65536, k_hashes: int = 4):
        self.size = size
        self.k = k_hashes
        self.counters = [0] * size

    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.md5(f"{item}_{seed}".encode("utf-8")).hexdigest()
        return int(h, 16) % self.size

    def add(self, item: str) -> None:
        """Insert an item by incrementing k counters."""
        for i in range(self.k):
            idx = self._hash(item, i)
            self.counters[idx] += 1

    def contains(self, item: str) -> bool:
        """Check membership; returns False if definitively not in set."""
        for i in range(self.k):
            idx = self._hash(item, i)
            if self.counters[idx] == 0:
                return False
        return True

    def remove(self, item: str) -> bool:
        """Decrement k counters if item is present."""
        if not self.contains(item):
            return False
        for i in range(self.k):
            idx = self._hash(item, i)
            if self.counters[idx] > 0:
                self.counters[idx] -= 1
        return True
