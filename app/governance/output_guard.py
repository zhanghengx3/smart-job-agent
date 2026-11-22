"""OutputGuard —— AI 输出质量门禁"""
import json
import re
from typing import Any, Dict, Tuple
from pydantic import ValidationError


class OutputGuard:
    """输出质量校验"""

    @staticmethod
    def validate_structured_output(output: str, model_class: type) -> Tuple[bool, Any, str]:
        """
        校验结构化输出是否符合 Pydantic 模型
        返回：(是否通过, 解析结果/None, 错误信息)
        """
        # 1. 尝试从文本中提取 JSON
        json_str = OutputGuard._extract_json(output)
        if not json_str:
            return False, None, "未找到 JSON 格式输出"

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, None, f"JSON 解析失败：{e}"

        # 2. 用 Pydantic 校验
        try:
            result = model_class(**data)
        except ValidationError as e:
            return False, None, f"字段校验失败：{str(e)[:200]}"

        # 3. 业务规则校验
        biz_error = OutputGuard._business_check(result)
        if biz_error:
            return False, result, biz_error

        return True, result, ""

    @staticmethod
    def _extract_json(text: str) -> str:
        """从文本中提取 JSON"""
        # 尝试直接解析
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text

        # 提取 ```json ... ``` 块
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()

        # 找第一个 { 和最后一个 }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace:last_brace + 1]

        return ""

    @staticmethod
    def _business_check(result: Any) -> str:
        """业务规则校验（根据不同模型扩展）"""
        # 通用校验：score 类字段在 0-100 之间
        if hasattr(result, "overall_score"):
            score = result.overall_score
            if score < 0 or score > 100:
                return f"overall_score 超出范围：{score}"

        return ""


# 全局 OutputGuard
output_guard = OutputGuard()