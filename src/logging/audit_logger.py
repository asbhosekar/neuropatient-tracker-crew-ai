"""
NeuroCrew AI - Clinical Audit Logger

HIPAA-compliant logging system for clinical AI applications.
Provides comprehensive audit trails for all agent interactions,
patient data access, and clinical decisions.
"""
import json
import logging
import os
import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from src.config import settings


# =============================================================================
# Enums for Audit Events
# =============================================================================

class AuditEventType(str, Enum):
    """Types of audit events for compliance tracking."""
    # System Events
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    
    # Authentication/Authorization
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    ACCESS_DENIED = "ACCESS_DENIED"
    
    # Patient Data Events (PHI)
    PHI_ACCESS = "PHI_ACCESS"
    PHI_CREATE = "PHI_CREATE"
    PHI_UPDATE = "PHI_UPDATE"
    PHI_DELETE = "PHI_DELETE"
    PHI_EXPORT = "PHI_EXPORT"
    PHI_QUERY = "PHI_QUERY"
    
    # Agent Events
    AGENT_INITIALIZED = "AGENT_INITIALIZED"
    AGENT_CONVERSATION_START = "AGENT_CONVERSATION_START"
    AGENT_CONVERSATION_END = "AGENT_CONVERSATION_END"
    AGENT_MESSAGE_SENT = "AGENT_MESSAGE_SENT"
    AGENT_MESSAGE_RECEIVED = "AGENT_MESSAGE_RECEIVED"
    AGENT_ERROR = "AGENT_ERROR"
    
    # Clinical Decision Events
    CLINICAL_RECOMMENDATION = "CLINICAL_RECOMMENDATION"
    PROGNOSIS_GENERATED = "PROGNOSIS_GENERATED"
    TREATMENT_SUGGESTED = "TREATMENT_SUGGESTED"
    REPORT_GENERATED = "REPORT_GENERATED"
    VALIDATION_PERFORMED = "VALIDATION_PERFORMED"
    
    # Data Quality Events
    DATA_VALIDATION_ERROR = "DATA_VALIDATION_ERROR"
    DATA_ANOMALY_DETECTED = "DATA_ANOMALY_DETECTED"


class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"  # Special level for compliance


# =============================================================================
# Custom Formatters
# =============================================================================

class HIPAACompliantFormatter(logging.Formatter):
    """
    Custom formatter that ensures no PHI is logged in plain text.
    Adds structured fields required for compliance.
    """
    
    def __init__(self):
        super().__init__()
        self.hostname = os.getenv("HOSTNAME", "localhost")
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON for compliance."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "hostname": self.hostname,
            "process_id": record.process,
            "thread_id": record.thread,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "event_type"):
            log_entry["event_type"] = record.event_type
        if hasattr(record, "session_id"):
            log_entry["session_id"] = record.session_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "patient_id_hash"):
            log_entry["patient_id_hash"] = record.patient_id_hash
        if hasattr(record, "agent_name"):
            log_entry["agent_name"] = record.agent_name
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "metadata"):
            log_entry["metadata"] = record.metadata
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter with colors."""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "AUDIT": "\033[34m",     # Blue
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build prefix with optional fields
        prefix_parts = [f"{color}[{record.levelname}]{self.RESET}"]
        
        if hasattr(record, "agent_name"):
            prefix_parts.append(f"[{record.agent_name}]")
        if hasattr(record, "event_type"):
            prefix_parts.append(f"<{record.event_type}>")
        
        prefix = " ".join(prefix_parts)
        
        return f"{timestamp} {prefix} {record.getMessage()}"


# =============================================================================
# Main Logger Classes
# =============================================================================

class ClinicalAuditLogger:
    """
    HIPAA-compliant clinical audit logger.
    
    Provides:
    - Structured JSON logging for audit trails
    - PHI redaction and hashing
    - Session tracking
    - Correlation IDs for distributed tracing
    - Separate audit log files
    - Log rotation and retention
    """
    
    _instance: Optional["ClinicalAuditLogger"] = None
    
    def __new__(cls):
        """Singleton pattern for consistent logging."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._session_id = str(uuid.uuid4())
        self._user_id: Optional[str] = None
        
        # Create logs directory
        self.logs_dir = Path(settings.LOGS_DIR)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Set up all required loggers."""
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        
        # Main application logger
        self.app_logger = logging.getLogger("neurocrew.app")
        self.app_logger.setLevel(log_level)
        
        # Audit logger (always INFO level for compliance)
        self.audit_logger = logging.getLogger("neurocrew.audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # Agent conversation logger
        self.agent_logger = logging.getLogger("neurocrew.agents")
        self.agent_logger.setLevel(log_level)
        
        # PHI access logger (critical - always enabled)
        self.phi_logger = logging.getLogger("neurocrew.phi")
        self.phi_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for logger in [self.app_logger, self.audit_logger, self.agent_logger, self.phi_logger]:
            logger.handlers.clear()
        
        # Add handlers
        self._add_handlers()
    
    def _add_handlers(self):
        """Add file and console handlers."""
        # Console handler (human-readable)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ConsoleFormatter())
        
        if settings.DEBUG:
            self.app_logger.addHandler(console_handler)
            self.agent_logger.addHandler(console_handler)
        
        # Main app log file (rotating by size - 10MB, keep 10 files)
        app_file_handler = RotatingFileHandler(
            self.logs_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding="utf-8",
        )
        app_file_handler.setFormatter(HIPAACompliantFormatter())
        self.app_logger.addHandler(app_file_handler)
        
        # Audit log file (rotating daily, keep 365 days for compliance)
        audit_file_handler = TimedRotatingFileHandler(
            self.logs_dir / "audit.log",
            when="midnight",
            interval=1,
            backupCount=365,  # Keep 1 year of audit logs
            encoding="utf-8",
        )
        audit_file_handler.setFormatter(HIPAACompliantFormatter())
        self.audit_logger.addHandler(audit_file_handler)
        
        # Agent conversation log (rotating by size)
        agent_file_handler = RotatingFileHandler(
            self.logs_dir / "agents.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=20,
            encoding="utf-8",
        )
        agent_file_handler.setFormatter(HIPAACompliantFormatter())
        self.agent_logger.addHandler(agent_file_handler)
        
        # PHI access log (critical - daily rotation, keep 7 years)
        phi_file_handler = TimedRotatingFileHandler(
            self.logs_dir / "phi_access.log",
            when="midnight",
            interval=1,
            backupCount=365 * 7,  # Keep 7 years per HIPAA
            encoding="utf-8",
        )
        phi_file_handler.setFormatter(HIPAACompliantFormatter())
        self.phi_logger.addHandler(phi_file_handler)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    @staticmethod
    def hash_phi(value: str) -> str:
        """
        Create a one-way hash of PHI for logging.
        Never log actual PHI - only hashed values.
        """
        if not value:
            return "EMPTY"
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    def set_user(self, user_id: str):
        """Set the current user for audit trail."""
        self._user_id = user_id
    
    def new_correlation_id(self) -> str:
        """Generate a new correlation ID for request tracking."""
        return str(uuid.uuid4())
    
    def _create_extra(
        self,
        event_type: AuditEventType,
        patient_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create extra fields for log record."""
        extra = {
            "event_type": event_type.value,
            "session_id": self._session_id,
        }
        
        if self._user_id:
            extra["user_id"] = self._user_id
        if patient_id:
            extra["patient_id_hash"] = self.hash_phi(patient_id)
        if agent_name:
            extra["agent_name"] = agent_name
        if correlation_id:
            extra["correlation_id"] = correlation_id
        if duration_ms is not None:
            extra["duration_ms"] = duration_ms
        if metadata:
            extra["metadata"] = metadata
        
        return extra
    
    # =========================================================================
    # Audit Event Logging
    # =========================================================================
    
    def log_system_start(self):
        """Log system startup."""
        extra = self._create_extra(AuditEventType.SYSTEM_START)
        self.audit_logger.info(
            "NeuroCrew AI system started",
            extra=extra,
        )
    
    def log_system_stop(self):
        """Log system shutdown."""
        extra = self._create_extra(AuditEventType.SYSTEM_STOP)
        self.audit_logger.info(
            "NeuroCrew AI system stopped",
            extra=extra,
        )
    
    def log_agent_initialized(self, agent_name: str):
        """Log agent initialization."""
        extra = self._create_extra(
            AuditEventType.AGENT_INITIALIZED,
            agent_name=agent_name,
        )
        self.agent_logger.info(
            f"Agent initialized: {agent_name}",
            extra=extra,
        )
    
    def log_conversation_start(
        self,
        correlation_id: str,
        task_summary: str,
        agents_involved: list[str],
    ):
        """Log start of multi-agent conversation."""
        extra = self._create_extra(
            AuditEventType.AGENT_CONVERSATION_START,
            correlation_id=correlation_id,
            metadata={"agents": agents_involved, "task_summary": task_summary[:200]},
        )
        self.audit_logger.info(
            f"Conversation started with {len(agents_involved)} agents",
            extra=extra,
        )
    
    def log_conversation_end(
        self,
        correlation_id: str,
        duration_ms: float,
        message_count: int,
        termination_reason: str,
    ):
        """Log end of multi-agent conversation."""
        extra = self._create_extra(
            AuditEventType.AGENT_CONVERSATION_END,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            metadata={
                "message_count": message_count,
                "termination_reason": termination_reason,
            },
        )
        self.audit_logger.info(
            f"Conversation ended: {message_count} messages in {duration_ms:.0f}ms",
            extra=extra,
        )
    
    def log_agent_message(
        self,
        agent_name: str,
        message_type: str,  # "sent" or "received"
        correlation_id: str,
        content_length: int,
        patient_id: Optional[str] = None,
    ):
        """Log individual agent message."""
        event_type = (
            AuditEventType.AGENT_MESSAGE_SENT
            if message_type == "sent"
            else AuditEventType.AGENT_MESSAGE_RECEIVED
        )
        extra = self._create_extra(
            event_type,
            agent_name=agent_name,
            correlation_id=correlation_id,
            patient_id=patient_id,
            metadata={"content_length": content_length},
        )
        self.agent_logger.debug(
            f"{agent_name} {message_type} message ({content_length} chars)",
            extra=extra,
        )
    
    def log_phi_access(
        self,
        patient_id: str,
        access_type: str,  # "read", "write", "delete"
        data_fields: list[str],
        reason: str,
    ):
        """
        Log PHI access - CRITICAL for HIPAA compliance.
        Every access to patient data must be logged.
        """
        event_map = {
            "read": AuditEventType.PHI_ACCESS,
            "write": AuditEventType.PHI_UPDATE,
            "create": AuditEventType.PHI_CREATE,
            "delete": AuditEventType.PHI_DELETE,
            "export": AuditEventType.PHI_EXPORT,
            "query": AuditEventType.PHI_QUERY,
        }
        event_type = event_map.get(access_type, AuditEventType.PHI_ACCESS)
        
        extra = self._create_extra(
            event_type,
            patient_id=patient_id,
            metadata={
                "access_type": access_type,
                "fields_accessed": data_fields,
                "access_reason": reason,
            },
        )
        self.phi_logger.info(
            f"PHI {access_type}: patient {self.hash_phi(patient_id)}, fields: {data_fields}",
            extra=extra,
        )
    
    def log_clinical_recommendation(
        self,
        agent_name: str,
        recommendation_type: str,
        patient_id: Optional[str],
        correlation_id: str,
        confidence: Optional[float] = None,
    ):
        """Log clinical recommendations made by agents."""
        extra = self._create_extra(
            AuditEventType.CLINICAL_RECOMMENDATION,
            agent_name=agent_name,
            patient_id=patient_id,
            correlation_id=correlation_id,
            metadata={
                "recommendation_type": recommendation_type,
                "confidence": confidence,
            },
        )
        self.audit_logger.info(
            f"Clinical recommendation: {recommendation_type} by {agent_name}",
            extra=extra,
        )
    
    def log_prognosis_generated(
        self,
        patient_id: str,
        correlation_id: str,
        trend: str,
        confidence: float,
    ):
        """Log prognosis analysis generation."""
        extra = self._create_extra(
            AuditEventType.PROGNOSIS_GENERATED,
            patient_id=patient_id,
            correlation_id=correlation_id,
            metadata={"trend": trend, "confidence": confidence},
        )
        self.audit_logger.info(
            f"Prognosis generated: {trend} (confidence: {confidence:.2f})",
            extra=extra,
        )
    
    def log_report_generated(
        self,
        report_type: str,
        patient_id: Optional[str],
        correlation_id: str,
    ):
        """Log report generation."""
        extra = self._create_extra(
            AuditEventType.REPORT_GENERATED,
            patient_id=patient_id,
            correlation_id=correlation_id,
            metadata={"report_type": report_type},
        )
        self.audit_logger.info(
            f"Report generated: {report_type}",
            extra=extra,
        )
    
    def log_validation_error(
        self,
        validation_type: str,
        field: str,
        error_message: str,
        patient_id: Optional[str] = None,
    ):
        """Log data validation errors."""
        extra = self._create_extra(
            AuditEventType.DATA_VALIDATION_ERROR,
            patient_id=patient_id,
            metadata={
                "validation_type": validation_type,
                "field": field,
                "error": error_message,
            },
        )
        self.audit_logger.warning(
            f"Validation error in {field}: {error_message}",
            extra=extra,
        )
    
    def log_error(
        self,
        error_message: str,
        exception: Optional[Exception] = None,
        agent_name: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """Log errors with full context."""
        extra = self._create_extra(
            AuditEventType.AGENT_ERROR,
            agent_name=agent_name,
            correlation_id=correlation_id,
        )
        self.app_logger.error(
            error_message,
            exc_info=exception,
            extra=extra,
        )


# =============================================================================
# Decorators for Easy Logging
# =============================================================================

def log_phi_access(access_type: str, fields: list[str], reason: str):
    """
    Decorator to automatically log PHI access.
    
    Usage:
        @log_phi_access("read", ["name", "dob"], "Patient lookup")
        def get_patient(patient_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            patient_id = kwargs.get("patient_id") or (args[0] if args else None)
            
            if patient_id:
                logger.log_phi_access(
                    patient_id=str(patient_id),
                    access_type=access_type,
                    data_fields=fields,
                    reason=reason,
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_agent_execution(func: Callable) -> Callable:
    """
    Decorator to log agent method execution with timing.
    
    Usage:
        @log_agent_execution
        async def run_analysis(self, data):
            ...
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        logger = get_logger()
        agent_name = getattr(self, "name", self.__class__.__name__)
        correlation_id = logger.new_correlation_id()
        start_time = datetime.now()
        
        logger.agent_logger.info(
            f"Starting {func.__name__}",
            extra=logger._create_extra(
                AuditEventType.AGENT_MESSAGE_SENT,
                agent_name=agent_name,
                correlation_id=correlation_id,
            ),
        )
        
        try:
            result = await func(self, *args, **kwargs)
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.agent_logger.info(
                f"Completed {func.__name__}",
                extra=logger._create_extra(
                    AuditEventType.AGENT_MESSAGE_RECEIVED,
                    agent_name=agent_name,
                    correlation_id=correlation_id,
                    duration_ms=duration_ms,
                ),
            )
            return result
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.log_error(
                f"Error in {func.__name__}: {str(e)}",
                exception=e,
                agent_name=agent_name,
                correlation_id=correlation_id,
            )
            raise
    
    return wrapper


# =============================================================================
# Module-level accessor
# =============================================================================

_logger_instance: Optional[ClinicalAuditLogger] = None


def get_logger() -> ClinicalAuditLogger:
    """Get the singleton logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ClinicalAuditLogger()
    return _logger_instance


def init_logging():
    """Initialize the logging system. Call at application startup."""
    logger = get_logger()
    logger.log_system_start()
    return logger
