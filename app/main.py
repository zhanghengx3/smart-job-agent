"""FastAPI 入口"""
import sys
import os
from pathlib import Path

# 路径兼容
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import config
from app.logger_setup import setup_logger
from app.api.chat import router as chat_router
from app.api.health import router as health_router

# 初始化日志
logger = setup_logger(
    log_dir=os.path.join(PROJECT_ROOT, "logs"),
    level=config.LOG_LEVEL,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动和关闭时的钩子"""
    logger.info("🚀 JobAgent 服务启动中...")
    logger.info(f"📦 模型：{config.LLM_MODEL}")
    logger.info(f"🌐 端口：{config.PORT}")
    yield
    logger.info("👋 服务已关闭")

app = FastAPI(
    title="JobAgent - 智能求职助手",
    description="基于多智能体的个性化求职平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health_router, prefix="/api", tags=["健康检查"])
app.include_router(chat_router, prefix="/api", tags=["求职分析"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )