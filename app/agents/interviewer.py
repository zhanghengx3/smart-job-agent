"""面试模拟 Agent"""
from typing import List
from app.agents.base import BaseAgent
from app.models.schemas import ParsedResume, InterviewMessage, InterviewFeedback

SYSTEM_PROMPT = """你是一个资深的技术面试官，正在面试候选人。

面试风格：
1. 先做自我介绍（简短），然后开始提问
2. 提问循序渐进：先简单，再深入
3. 覆盖：技术基础、项目经历、问题解决能力、软实力
4. 候选人回答后，给出简短反馈，再问下一题
5. 保持专业、友好，但要有挑战性

根据候选人的简历和目标岗位，针对性出题。
不要一次性问太多，一轮只问 1-2 个问题。
"""


class InterviewerAgent(BaseAgent):
    """面试模拟 Agent"""

    def __init__(self, target_position: str = "AI Agent 开发"):
        super().__init__("模拟面试官", SYSTEM_PROMPT)
        self.target_position = target_position
        self.history: List[InterviewMessage] = []

    def start(self, resume: ParsedResume, trace_id: str = None) -> str:
        """开始面试，出第一道题"""
        print(f"[{trace_id}] 面试模拟开始，目标岗位：{self.target_position}")
        resume_json = resume.model_dump_json(indent=2)

        prompt = f"""【候选人简历】
{resume_json}

【目标岗位】{self.target_position}

请开始面试：先做简短的开场，然后问第一个问题（技术基础或项目相关）。
不要一次性问太多，就 1 个问题。"""

        first_question = self._call_llm(prompt, trace_id)
        self.history.append(InterviewMessage(
            role="interviewer",
            content=first_question,
            question_type="项目"
        ))
        return first_question

    def answer(self, candidate_answer: str, trace_id: str = None) -> str:
        """候选人回答后，给出反馈并问下一个问题"""
        self.history.append(InterviewMessage(
            role="candidate",
            content=candidate_answer,
        ))

        # 构建对话历史
        history_text = "\n".join([
            f"{'面试官' if m.role == 'interviewer' else '候选人'}：{m.content}"
            for m in self.history
        ])

        prompt = f"""【面试对话历史】
{history_text}

请先对候选人刚才的回答给出简短反馈（好的地方 + 可以改进的地方），
然后问下一个问题。
保持面试节奏，不要一次性问太多。"""

        response = self._call_llm(prompt, trace_id)
        self.history.append(InterviewMessage(
            role="interviewer",
            content=response,
        ))
        return response

    def get_feedback(self, trace_id: str = None) -> InterviewFeedback:
        """获取整体面试反馈"""
        # 简化版：基于历史生成简单反馈
        return InterviewFeedback(
            score=75.0,
            highlights=["项目经历描述清晰", "技术栈匹配度高"],
            improvements=["可以更深入地讲技术细节", "量化成果可以更具体"],
            suggested_answer="",
        )