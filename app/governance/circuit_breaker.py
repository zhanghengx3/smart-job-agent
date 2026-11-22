"""熔断器 —— 失败次数达到阈值就熔断"""
import time
import threading
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"  # 正常
    OPEN = "open"  # 熔断
    HALF_OPEN = "half_open"  # 半开（试探）


class CircuitBreaker:
    """熔断器"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """当前状态"""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time > self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
            return self._state

    def can_execute(self) -> bool:
        """是否允许执行"""
        return self.state != CircuitState.OPEN

    def record_success(self):
        """记录成功"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
            self._failure_count = 0

    def record_failure(self):
        """记录失败"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN


# 全局熔断器（LLM 调用用）
llm_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)