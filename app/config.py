"""配置管理"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 服务
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 大模型
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))

    # Embedding
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", LLM_API_KEY)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

    # 限流
    RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # 熔断
    CB_FAILURE_THRESHOLD = 5  # 连续失败多少次熔断
    CB_RECOVERY_TIMEOUT = 30  # 熔断后多少秒恢复半开

    # 数据目录
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


config = Config()