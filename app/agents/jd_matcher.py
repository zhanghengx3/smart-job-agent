"""JD 匹配 Agent"""
from app.agents.base import BaseAgent
from app.models.schemas import ParsedResume, MatchResult, MatchDimension
from app.governance.output_guard import output_guard

SYSTEM_PROMPT = """你是一个专业的招聘匹配分析师。
请根据候选人简历和岗位 JD，进行多维度的人岗匹配分析。

分析维度：
1. 技能匹配（权重 35%）：技术栈、工具、框架的匹配度
2. 项目经验匹配（权重 30%）：项目经历与岗位要求的相关度
3. 学历/专业匹配（权重 15%）：学历层次、专业对口度
4. 综合软实力（权重 20%）：学习能力、沟通、潜力等

要求：
1. 严格输出 JSON 格式
2. 每个维度要有得分（0-100）、权重、详细说明、差距点
3. 总体得分是加权平均
4. 优势、劣势、建议各列 3-5 条，要具体

输出 JSON 格式：
{
  "overall_score": 85,
  "dimensions": [
    {
      "name": "技能匹配",
      "score": 80,
      "weight": 0.35,
      "details": "候选人掌握 Python、FastAPI、LangChain 等核心技能...",
      "gaps": ["缺少 Kubernetes 经验", "Redis 不熟悉"]
    }
  ],
  "strengths": ["优势1", "优势2", "优势3"],
  "weaknesses": ["劣势1", "劣势2"],
  "suggestions": ["建议1", "建议2", "建议3"]
}
"""


class JDMatcherAgent(BaseAgent):
    """JD 匹配 Agent"""

    def __init__(self):
        super().__init__("JD 匹配 Agent", SYSTEM_PROMPT)

    def run(
            self,
            resume: ParsedResume,
            jd_text: str,
            trace_id: str = None
    ) -> MatchResult:
        """进行人岗匹配分析"""
        logger_info = f"[{trace_id}] " if trace_id else ""
        print(f"{logger_info}JD 匹配 Agent 开始工作...")

        resume_json = resume.model_dump_json(indent=2)
        prompt = f"""【候选人简历】
{resume_json}

【岗位 JD】
{jd_text}

请进行详细的人岗匹配分析。"""

        raw_output = self._call_llm(prompt, trace_id)

        # 质量门禁
        passed, result, error = output_guard.validate_structured_output(
            raw_output, MatchResult
        )

        if not passed:
            print(f"{logger_info}⚠️ 匹配分析 OutputGuard 校验失败：{error}")
            result = MatchResult(
                overall_score=60.0,
                dimensions=[
                    MatchDimension(
                        name="初步评估",
                        score=60,
                        weight=1.0,
                        details="系统繁忙，仅提供初步评估",
                        gaps=["系统繁忙，详细分析暂不可用"]
                    )
                ],
                strengths=["有相关项目经验"],
                weaknesses=["系统繁忙，分析不完整"],
                suggestions=["稍后再试"],
            )

        print(f"{logger_info}✅ 匹配分析完成，总分：{result.overall_score}")
        return result