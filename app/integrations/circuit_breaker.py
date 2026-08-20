import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 10,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = None

        self.state = CircuitState.CLOSED

    def can_execute(self) -> bool:

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:

            if (
                self.last_failure_time
                and time.time() - self.last_failure_time
                >= self.recovery_timeout
            ):
                self.state = CircuitState.HALF_OPEN
                return True

            return False

        # HALF_OPEN
        return True

    def record_success(self):

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def record_failure(self):

        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN