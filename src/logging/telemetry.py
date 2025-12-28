"""
NeuroCrew AI - Runtime Telemetry

OpenTelemetry-based runtime logging for LLM performance,
token usage, and cost tracking.
"""
import logging
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field, asdict
from functools import wraps
import time

from src.config import settings


# =============================================================================
# Token Cost Tracking
# =============================================================================

# Pricing per 1K tokens (as of late 2024 - update as needed)
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}


@dataclass
class LLMCallMetrics:
    """Metrics for a single LLM API call."""
    call_id: str
    timestamp: str
    model: str
    agent_name: Optional[str] = None
    
    # Token counts
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Timing
    latency_ms: float = 0.0
    
    # Cost
    estimated_cost_usd: float = 0.0
    
    # Request details
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    # Response info
    finish_reason: Optional[str] = None
    
    # Error tracking
    error: Optional[str] = None
    success: bool = True


@dataclass  
class SessionMetrics:
    """Aggregated metrics for a session."""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    
    # Totals
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    
    # Token totals
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    
    # Cost totals
    total_cost_usd: float = 0.0
    
    # Timing
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    
    # By agent breakdown
    calls_by_agent: dict = field(default_factory=dict)
    tokens_by_agent: dict = field(default_factory=dict)
    cost_by_agent: dict = field(default_factory=dict)


# =============================================================================
# Telemetry Logger
# =============================================================================

class RuntimeTelemetry:
    """
    Runtime telemetry for LLM performance and cost tracking.
    
    Tracks:
    - Token usage per call and session
    - API latency
    - Cost estimation
    - Error rates
    - Per-agent metrics
    """
    
    _instance: Optional["RuntimeTelemetry"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self._session_metrics = SessionMetrics(
            session_id=self._session_id,
            start_time=datetime.now(timezone.utc).isoformat(),
        )
        self._call_history: list[LLMCallMetrics] = []
        self._call_counter = 0
        
        # Setup logging directory
        self.logs_dir = Path(settings.LOGS_DIR)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup AutoGen trace logger
        self._setup_autogen_tracing()
        
        # Setup telemetry file logger
        self._setup_file_logger()
    
    def _setup_autogen_tracing(self):
        """Enable AutoGen's built-in trace logging."""
        try:
            from autogen_core import TRACE_LOGGER_NAME
            trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
            trace_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
            
            # Add file handler for autogen traces
            handler = logging.FileHandler(
                self.logs_dir / "autogen_trace.log",
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            trace_logger.addHandler(handler)
            
        except ImportError:
            # TRACE_LOGGER_NAME might not exist in all versions
            pass
    
    def _setup_file_logger(self):
        """Setup telemetry file logger."""
        self.telemetry_logger = logging.getLogger("neurocrew.telemetry")
        self.telemetry_logger.setLevel(logging.INFO)
        self.telemetry_logger.handlers.clear()
        
        handler = logging.FileHandler(
            self.logs_dir / "llm_telemetry.jsonl",
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.telemetry_logger.addHandler(handler)
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost for an LLM call."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING.get("gpt-4o-mini"))
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        return round(input_cost + output_cost, 6)
    
    def _generate_call_id(self) -> str:
        """Generate unique call ID."""
        self._call_counter += 1
        return f"{self._session_id}_{self._call_counter:04d}"
    
    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        agent_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        finish_reason: Optional[str] = None,
        error: Optional[str] = None,
    ) -> LLMCallMetrics:
        """
        Log an LLM API call with all metrics.
        
        Args:
            model: Model name used
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            latency_ms: API latency in milliseconds
            agent_name: Name of the agent making the call
            temperature: Temperature parameter used
            max_tokens: Max tokens parameter
            finish_reason: Why the response ended
            error: Error message if call failed
            
        Returns:
            LLMCallMetrics with all recorded data
        """
        total_tokens = prompt_tokens + completion_tokens
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens) if not error else 0.0
        
        metrics = LLMCallMetrics(
            call_id=self._generate_call_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            model=model,
            agent_name=agent_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            estimated_cost_usd=cost,
            temperature=temperature,
            max_tokens=max_tokens,
            finish_reason=finish_reason,
            error=error,
            success=error is None,
        )
        
        # Store in history
        self._call_history.append(metrics)
        
        # Update session metrics
        self._update_session_metrics(metrics)
        
        # Log to file
        self.telemetry_logger.info(json.dumps(asdict(metrics)))
        
        return metrics
    
    def _update_session_metrics(self, call: LLMCallMetrics):
        """Update aggregated session metrics."""
        s = self._session_metrics
        
        s.total_calls += 1
        if call.success:
            s.successful_calls += 1
        else:
            s.failed_calls += 1
        
        s.total_prompt_tokens += call.prompt_tokens
        s.total_completion_tokens += call.completion_tokens
        s.total_tokens += call.total_tokens
        s.total_cost_usd += call.estimated_cost_usd
        s.total_latency_ms += call.latency_ms
        s.avg_latency_ms = s.total_latency_ms / s.total_calls
        
        # By agent tracking
        agent = call.agent_name or "unknown"
        s.calls_by_agent[agent] = s.calls_by_agent.get(agent, 0) + 1
        s.tokens_by_agent[agent] = s.tokens_by_agent.get(agent, 0) + call.total_tokens
        s.cost_by_agent[agent] = s.cost_by_agent.get(agent, 0) + call.estimated_cost_usd
    
    def get_session_summary(self) -> dict:
        """Get current session metrics summary."""
        s = self._session_metrics
        s.end_time = datetime.now(timezone.utc).isoformat()
        return asdict(s)
    
    def get_cost_report(self) -> str:
        """Generate a human-readable cost report."""
        s = self._session_metrics
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              NeuroCrew AI - Session Cost Report              ║
╠══════════════════════════════════════════════════════════════╣
║ Session ID: {s.session_id:<47} ║
║ Duration: {s.start_time[:19]} to now                       ║
╠══════════════════════════════════════════════════════════════╣
║ CALLS                                                        ║
║   Total:      {s.total_calls:<10} Success: {s.successful_calls:<10} Failed: {s.failed_calls:<5} ║
╠══════════════════════════════════════════════════════════════╣
║ TOKENS                                                       ║
║   Prompt:     {s.total_prompt_tokens:<15,}                             ║
║   Completion: {s.total_completion_tokens:<15,}                             ║
║   Total:      {s.total_tokens:<15,}                             ║
╠══════════════════════════════════════════════════════════════╣
║ COST                                                         ║
║   Estimated:  ${s.total_cost_usd:<10.4f} USD                            ║
╠══════════════════════════════════════════════════════════════╣
║ PERFORMANCE                                                  ║
║   Avg Latency: {s.avg_latency_ms:,.0f} ms                                  ║
╠══════════════════════════════════════════════════════════════╣
║ BY AGENT                                                     ║"""
        
        for agent, tokens in s.tokens_by_agent.items():
            cost = s.cost_by_agent.get(agent, 0)
            calls = s.calls_by_agent.get(agent, 0)
            report += f"\n║   {agent:<15} {calls:>3} calls  {tokens:>8,} tokens  ${cost:.4f}  ║"
        
        report += """
╚══════════════════════════════════════════════════════════════╝"""
        
        return report
    
    def save_session_report(self):
        """Save final session report to file."""
        report_file = self.logs_dir / f"session_{self._session_id}_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.get_session_summary(), f, indent=2)
        
        # Also save human-readable report
        txt_file = self.logs_dir / f"session_{self._session_id}_report.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(self.get_cost_report())
    
    def print_cost_summary(self):
        """Print cost summary to console."""
        print(self.get_cost_report())


# =============================================================================
# LLM Call Wrapper with Telemetry
# =============================================================================

def track_llm_call(agent_name: Optional[str] = None):
    """
    Decorator to track LLM calls with telemetry.
    
    Usage:
        @track_llm_call("Neurologist")
        async def generate_response(self, prompt):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            start_time = time.time()
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                
                # Try to extract token info from result if available
                # This is a placeholder - actual implementation depends on response format
                telemetry.log_llm_call(
                    model=settings.OPENAI_MODEL,
                    prompt_tokens=0,  # Would need to extract from response
                    completion_tokens=0,
                    latency_ms=latency_ms,
                    agent_name=agent_name,
                    error=error,
                )
        return wrapper
    return decorator


# =============================================================================
# OpenTelemetry Integration (Optional)
# =============================================================================

def setup_opentelemetry(service_name: str = "neurocrew-ai") -> bool:
    """
    Setup OpenTelemetry for distributed tracing.
    
    Returns True if setup successful, False otherwise.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource
        
        # Create resource with service name
        resource = Resource.create({"service.name": service_name})
        
        # Setup tracer provider
        provider = TracerProvider(resource=resource)
        
        # Add console exporter for debugging (can add file/OTLP exporters)
        if settings.DEBUG:
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(provider)
        
        return True
        
    except ImportError:
        # OpenTelemetry not installed
        return False


def get_tracer(name: str = "neurocrew"):
    """Get OpenTelemetry tracer."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        return None


# =============================================================================
# Module-level accessor
# =============================================================================

_telemetry_instance: Optional[RuntimeTelemetry] = None


def get_telemetry() -> RuntimeTelemetry:
    """Get the singleton telemetry instance."""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = RuntimeTelemetry()
    return _telemetry_instance


def init_telemetry() -> RuntimeTelemetry:
    """Initialize telemetry system. Call at application startup."""
    telemetry = get_telemetry()
    setup_opentelemetry()
    return telemetry
