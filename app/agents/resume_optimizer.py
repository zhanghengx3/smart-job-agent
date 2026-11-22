"""简历优化 Agent"""
from app.agents.base import BaseAgent
from app.models.schemas import ParsedResume, ResumeOptimization, OptimizationSuggestion
from app.governance.output_guard import output_guard

SYSTEM_PROMPT = """你是一个资深的简历优化顾问，有 10 年 HR 和招聘经验。
请根据候选人简历和目标岗位，给出针对性的简历优化建议。

优化原则：
1. STAR 法则：情境-任务-行动-结果
2. 量化成果：用数字说话（百分比、金额、效率提升）
3. 关键词匹配：突出岗位要求的核心技能
4. 行动动词开头：主导、设计、实现、优化、搭建...
5. 不造假、不夸大，基于事实优化表达

要求：
1. 严格输出 JSON 格式
2. 给出 5-8 条具体优化建议，每条要有原文、优化后、理由
3. 按优先级排序（高/中/低）
4. 给出优化前得分和预计优化后得分
5. 核心改进点列 3-5 条

输出 JSON 格式：
{
  "overall_score": 65,
  "estimated_score": 85,
  "suggestions": [
    {
      "section": "项目",
      "original": "负责电商监控系统开发",
      "optimized": "主导设计并实现基于 LangGraph 的电商商品智能监控系统，采用双 Agent 架构，将异常检出率提升至 95%+",
      "reason": "使用行动动词开头，补充技术栈和量化成果，更有冲击力",
      "priority": "高"
    }
  ],
  "key_improvements": ["核心改进1", "核心改进2", "核心改进3"]
}
"""


class ResumeOptimizerAgent(BaseAgent):
    """简历优化 Agent"""

    def __init__(self):
        super().__init__("简历优化 Agent", SYSTEM_PROMPT)

    def run(
            self,
            resume: ParsedResume,
            target_position: str = None,
            trace_id: str = None
    ) -> ResumeOptimization:
        """生成简历优化建议"""
        logger_info = f"[{trace_id}] " if trace_id else ""
        print(f"{logger_info}简历优化 Agent 开始工作...")

        resume_json = resume.model_dump_json(indent=2)
        target = target_position or resume.target_position

        prompt = f"""【候选人简历】
{resume_json}

【目标岗位】
{target}

请给出针对性的简历优化建议。"""

        raw_output = self._call_llm(prompt, trace_id)

        # 质量门禁
        passed, result, error = output_guard.validate_structured_output(
            raw_output, ResumeOptimization
        )

        if not passed:
            print(f"{logger_info}⚠️ 简历优化 OutputGuard 校验失败：{error}")
            result = ResumeOptimization(
                overall_score=60.0,
                estimated_score=75.0,
                suggestions=[],
                key_improvements=["系统繁忙，建议稍后再试"],
            )

        print(f"{logger_info}✅ 简历优化完成，预计提升：{result.estimated_score - result.overall_score} 分")
        return result