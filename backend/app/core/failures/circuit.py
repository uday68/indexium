import time
from enum import Enum
from typing import Callable, Any, Optional


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    """Protects external or slow services using the Circuit Breaker pattern."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_sec: float = 30.0,
        half_open_success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_sec
        self.half_open_threshold = half_open_success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()

        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.last_state_change = now
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN. Fast failing request.")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
