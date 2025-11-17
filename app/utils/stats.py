"""Statistics tracking for API usage and token counts."""

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class RequestStats:
    """Statistics for a single request."""
    timestamp: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    finish_reason: str


@dataclass
class AggregateStats:
    """Aggregate statistics."""
    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    requests_by_model: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tokens_by_model: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    finish_reasons: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recent_requests: deque = field(default_factory=lambda: deque(maxlen=100))  # Keep last 100 requests


class StatsTracker:
    """Thread-safe statistics tracker."""
    
    def __init__(self):
        self._lock = Lock()
        self._stats = AggregateStats()
        self._start_time = time.time()
    
    def record_request(self, stats: RequestStats):
        """Record a request's statistics."""
        with self._lock:
            self._stats.total_requests += 1
            self._stats.total_prompt_tokens += stats.prompt_tokens
            self._stats.total_completion_tokens += stats.completion_tokens
            self._stats.total_tokens += stats.total_tokens
            self._stats.requests_by_model[stats.model] += 1
            self._stats.tokens_by_model[stats.model] += stats.total_tokens
            self._stats.finish_reasons[stats.finish_reason] += 1
            self._stats.recent_requests.append(stats)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self._lock:
            uptime_seconds = time.time() - self._start_time
            uptime_hours = uptime_seconds / 3600
            
            # Calculate averages
            avg_prompt_tokens = (
                self._stats.total_prompt_tokens / self._stats.total_requests
                if self._stats.total_requests > 0 else 0
            )
            avg_completion_tokens = (
                self._stats.total_completion_tokens / self._stats.total_requests
                if self._stats.total_requests > 0 else 0
            )
            avg_total_tokens = (
                self._stats.total_tokens / self._stats.total_requests
                if self._stats.total_requests > 0 else 0
            )
            
            # Calculate requests per hour
            requests_per_hour = (
                self._stats.total_requests / uptime_hours
                if uptime_hours > 0 else 0
            )
            
            # Calculate tokens per hour
            tokens_per_hour = (
                self._stats.total_tokens / uptime_hours
                if uptime_hours > 0 else 0
            )
            
            return {
                "uptime_seconds": int(uptime_seconds),
                "uptime_hours": round(uptime_hours, 2),
                "total_requests": self._stats.total_requests,
                "total_prompt_tokens": self._stats.total_prompt_tokens,
                "total_completion_tokens": self._stats.total_completion_tokens,
                "total_tokens": self._stats.total_tokens,
                "average_prompt_tokens": round(avg_prompt_tokens, 2),
                "average_completion_tokens": round(avg_completion_tokens, 2),
                "average_total_tokens": round(avg_total_tokens, 2),
                "requests_per_hour": round(requests_per_hour, 2),
                "tokens_per_hour": round(tokens_per_hour, 2),
                "requests_by_model": dict(self._stats.requests_by_model),
                "tokens_by_model": dict(self._stats.tokens_by_model),
                "finish_reasons": dict(self._stats.finish_reasons),
                "recent_requests_count": len(self._stats.recent_requests),
            }
    
    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self._stats = AggregateStats()
            self._start_time = time.time()


# Global stats tracker instance
_stats_tracker = StatsTracker()


def get_stats_tracker() -> StatsTracker:
    """Get the global stats tracker instance."""
    return _stats_tracker

