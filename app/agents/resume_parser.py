"""简历解析 Agent"""
import json
from app.agents.base import BaseAgent
from app.models.schemas import ParsedResume
from app.governance.output_guard import output_guard

SYSTEM_PROMPT = """你是一个专业的简历解析专家。
请从用户提供的简历文本中，提取结构化信息。

要求：
1. 严格按照 JSON 格式输出，不要有多余的解释文字
2. 技能要分类，评估熟练程度（精通/熟练/了解）
3. 项目经历要提取技术栈和核心亮点
4. 信息要准确，没有的内容留空，不要编造

输出 JSON 格式：
{
  "name": "姓名",
  "target_position": "求职意向",
  "summary": "个人简介（总结 1-2 句话）",
  "skills": [
    {"name": "技能名", "level": "熟练", "projects": ["相关项目1"]}
  ],
  "education": [
    {"school": "学校", "major": "专业", "degree": "学历", "period": "2021-2025"}
  ],
  "projects": [
    {
      "name": "项目名",
      "role": "角色",
      "tech_stack": ["技术1", "技术2"],
      "highlights": ["亮点1", "亮点2"]
    }
  ]
}
"""


class ResumeParserAgent(BaseAgent):
    """简历解析 Agent"""

    def __init__(self):
        super().__init__("简历解析 Agent", SYSTEM_PROMPT)

    def run(self, resume_text: str, trace_id: str = None) -> ParsedResume:
        """解析简历"""
        logger_info = f"[{trace_id}] " if trace_id else ""
        print(f"{logger_info}简历解析 Agent 开始工作...")

        prompt = f"请解析以下简历：\n\n{resume_text}"
        raw_output = self._call_llm(prompt, trace_id)

        # 质量门禁校验
        passed, result, error = output_guard.validate_structured_output(
            raw_output, ParsedResume
        )

        if not passed:
            print(f"{logger_info}⚠️ 简历解析 OutputGuard 校验失败：{error}")
            # 降级：简单提取
            result = self._simple_extract(resume_text)

        print(f"{logger_info}✅ 简历解析完成，姓名：{result.name}")
        return result

    def _simple_extract(self, text: str) -> ParsedResume:
        """降级方案：简单提取"""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        name = lines[0] if lines else "未知"
        return ParsedResume(
            name=name,
            target_position="待分析",
            summary=text[:200] + "..." if len(text) > 200 else text,
        )