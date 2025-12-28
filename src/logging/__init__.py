"""
NeuroCrew AI - Logging Module

HIPAA-compliant audit logging and runtime telemetry for clinical AI applications.
"""

from .audit_logger import (
    ClinicalAuditLogger,
    AuditEventType,
    LogLevel,
    get_logger,
    init_logging,
    log_phi_access,
    log_agent_execution,
)

from .telemetry import (
    RuntimeTelemetry,
    LLMCallMetrics,
    SessionMetrics,
    get_telemetry,
    init_telemetry,
    track_llm_call,
    setup_opentelemetry,
)

__all__ = [
    # Audit Logging
    "ClinicalAuditLogger",
    "AuditEventType",
    "LogLevel",
    "get_logger",
    "init_logging",
    "log_phi_access",
    "log_agent_execution",
    # Telemetry
    "RuntimeTelemetry",
    "LLMCallMetrics",
    "SessionMetrics",
    "get_telemetry",
    "init_telemetry",
    "track_llm_call",
    "setup_opentelemetry",
]
