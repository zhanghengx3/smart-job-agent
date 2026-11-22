"""Agent 基类"""
import uuid
import time
import logging
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import config
from app.governance.circuit_breaker import llm_circuit_breaker

logger = logging.getLogger(__name__)


class BaseAgent:
    """Agent 基类"""

    def __init__(self, name: str, system_prompt: str, model: str = None):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model or config.LLM_MODEL
        self._llm = ChatOpenAI(
            model=self.model,
            temperature=config.LLM_TEMPERATURE,
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            timeout=config.LLM_TIMEOUT,
        )

    def _call_llm(self, user_input: str, trace_id: str = None) -> str:
        """调用 LLM（带熔断和重试）"""
        trace_id = trace_id or str(uuid.uuid4())
        max_retries = 3

        for attempt in range(max_retries):
            # 熔断检查
            if not llm_circuit_breaker.can_execute():
                logger.warning(f"[{trace_id}] {self.name} 熔断器已打开，降级处理")
                return self._fallback_response(user_input)

            try:
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_input),
                ]

                start_time = time.time()
                response = self._llm.invoke(messages)
                elapsed = time.time() - start_time

                llm_circuit_breaker.record_success()
                logger.info(
                    f"[{trace_id}] {self.name} LLM 调用成功 | "
                    f"耗时={elapsed:.2f}s | 尝试={attempt + 1}"
                )

                return response.content

            except Exception as e:
                llm_circuit_breaker.record_failure()
                logger.warning(
                    f"[{trace_id}] {self.name} LLM 调用失败 | "
                    f"尝试={attempt + 1}/{max_retries} | 错误={e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"[{trace_id}] {self.name} 全部重试失败")
                    return self._fallback_response(user_input)

    def _fallback_response(self, user_input: str) -> str:
        """降级响应（子类可以重写）"""
        return "抱歉，服务暂时不可用，请稍后再试。"

    def run(self, input_data: Any, trace_id: str = None) -> Any:
        """执行 Agent（子类重写）"""
        raise NotImplementedError