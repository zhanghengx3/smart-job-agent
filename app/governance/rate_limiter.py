"""限流器 —— 滑动窗口"""
import time
import threading
from collections import deque
from app.config import config


class RateLimiter:
    """滑动窗口限流器"""

    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests or config.RATE_LIMIT_MAX
        self.window_seconds = window_seconds or config.RATE_LIMIT_WINDOW
        self._requests = {}  # key -> deque of timestamps
        self._lock = threading.Lock()

    def check(self, key: str) -> bool:
        """检查是否允许通过"""
        now = time.time()
        with self._lock:
            if key not in self._requests:
                self._requests[key] = deque()

            dq = self._requests[key]
            # 移除窗口外的请求
            while dq and now - dq[0] > self.window_seconds:
                dq.popleft()

            if len(dq) < self.max_requests:
                dq.append(now)
                return True
            return False

    def remaining(self, key: str) -> int:
        """剩余可用次数"""
        now = time.time()
        with self._lock:
            if key not in self._requests:
                return self.max_requests
            dq = self._requests[key]
            while dq and now - dq[0] > self.window_seconds:
                dq.popleft()
            return max(0, self.max_requests - len(dq))


# 全局限流器
rate_limiter = RateLimiter()