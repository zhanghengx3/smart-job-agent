"""日志系统（简化版）"""
import os
import sys
import uuid
import logging
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler

from app.config import config

# 线程本地存储 Trace ID
_trace_local = threading.local()


def set_trace_id(trace_id: str = None) -> str:
    """设置 Trace ID"""
    if trace_id is None:
        trace_id = uuid.uuid4().hex[:8]
    _trace_local.trace_id = trace_id
    return trace_id


def get_trace_id() -> str:
    """获取 Trace ID"""
    return getattr(_trace_local, "trace_id", "")


class TraceIdFilter(logging.Filter):
    """注入 Trace ID"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id() or "-"
        return True


def setup_logger(log_dir: str = None, level: str = None) -> logging.Logger:
    """
    初始化日志系统

    :param log_dir: 日志目录，默认 data/logs
    :param level: 日志级别，默认 INFO
    """
    log_dir = log_dir or os.path.join(config.DATA_DIR, "logs")
    level = level or config.LOG_LEVEL

    os.makedirs(log_dir, exist_ok=True)

    # 日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    log_level = level_map.get(level.upper(), logging.INFO)

    # 根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    # 日志格式
    log_format = "%(asctime)s [%(levelname)s] [%(trace_id)s] %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 1. 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(TraceIdFilter())
    root_logger.addHandler(console_handler)

    # 2. 文件输出（按大小轮转）
    log_file = os.path.join(log_dir, "app.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=50 * 1024 * 1024,  # 单文件 50MB
        backupCount=30,  # 保留 30 个备份
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(TraceIdFilter())
    root_logger.addHandler(file_handler)

    # 3. 错误日志单独存
    error_file = os.path.join(log_dir, "error.log")
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=20 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(TraceIdFilter())
    root_logger.addHandler(error_handler)

    # 静音第三方库的啰嗦日志
    noisy = [
        "httpx", "httpcore", "urllib3",
        "langchain", "langchain_core", "langchain_community",
        "langchain_openai", "uvicorn", "fastapi", "starlette",
    ]
    for name in noisy:
        logging.getLogger(name).setLevel(logging.WARNING)

    logger = logging.getLogger("logger_setup")
    logger.info(
        f"日志系统已初始化 | 级别={level} | 目录={log_dir} | "
        f"保留30天 | 单文件最大50MB | 备份30个"
    )

    return root_logger