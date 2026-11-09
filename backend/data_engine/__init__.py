"""AI Auto Pakistan - Multi-Source Automotive Data Engineering Platform.

University Final Year Project (Department of Computer Science / Data Science).
Scalable dataset collection, engineering, quality validation, and AI preparation
tailored to the Pakistani automotive ecosystem.
"""

__version__ = "1.0.0"
__author__ = "AI Auto Pakistan Engineering Team"

from .config import DataEngineConfig, get_config
from .registry import SourceRegistry, DataSourceEntry, SourceType, RightsBasis
from .logger import AuditLogger, get_audit_logger

__all__ = [
    "DataEngineConfig",
    "get_config",
    "SourceRegistry",
    "DataSourceEntry",
    "SourceType",
    "RightsBasis",
    "AuditLogger",
    "get_audit_logger",
]
