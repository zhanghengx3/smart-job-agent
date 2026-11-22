"""数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ---------- 简历解析 ----------
class ResumeSkill(BaseModel):
    """技能项"""
    name: str = Field(description="技能名称")
    level: str = Field(description="熟练程度：熟练/了解/精通")
    projects: List[str] = Field(default_factory=list, description="相关项目")

class ResumeEducation(BaseModel):
    """教育经历"""
    school: str = Field(description="学校")
    major: str = Field(description="专业")
    degree: str = Field(description="学历")
    period: str = Field(description="时间段")

class ResumeProject(BaseModel):
    """项目经历"""
    name: str = Field(description="项目名称")
    role: str = Field(description="担任角色")
    tech_stack: List[str] = Field(default_factory=list, description="技术栈")
    highlights: List[str] = Field(default_factory=list, description="项目亮点")

class ParsedResume(BaseModel):
    """解析后的简历"""
    name: str = Field(description="姓名")
    target_position: str = Field(description="求职意向")
    skills: List[ResumeSkill] = Field(default_factory=list, description="技能列表")
    education: List[ResumeEducation] = Field(default_factory=list, description="教育经历")
    projects: List[ResumeProject] = Field(default_factory=list, description="项目经历")
    summary: str = Field(default="", description="个人简介")

# ---------- JD 匹配 ----------
class MatchDimension(BaseModel):
    """匹配维度"""
    name: str = Field(description="维度名称")
    score: float = Field(description="得分 0-100")
    weight: float = Field(description="权重")
    details: str = Field(description="详细说明")
    gaps: List[str] = Field(default_factory=list, description="差距/不足")

class MatchResult(BaseModel):
    """匹配结果"""
    overall_score: float = Field(description="总体匹配度 0-100")
    dimensions: List[MatchDimension] = Field(default_factory=list, description="各维度得分")
    strengths: List[str] = Field(default_factory=list, description="优势")
    weaknesses: List[str] = Field(default_factory=list, description="劣势")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")

# ---------- 简历优化 ----------
class OptimizationSuggestion(BaseModel):
    """优化建议"""
    section: str = Field(description="优化的模块：技能/项目/个人简介/整体")
    original: str = Field(description="原文")
    optimized: str = Field(description="优化后")
    reason: str = Field(description="优化理由")
    priority: str = Field(description="优先级：高/中/低")

class ResumeOptimization(BaseModel):
    """简历优化结果"""
    overall_score: float = Field(description="优化前得分 0-100")
    estimated_score: float = Field(description="预计优化后得分")
    suggestions: List[OptimizationSuggestion] = Field(default_factory=list, description="优化建议列表")
    key_improvements: List[str] = Field(default_factory=list, description="核心改进点")

# ---------- 面试模拟 ----------
class InterviewMessage(BaseModel):
    """面试消息"""
    role: str = Field(description="角色：interviewer/candidate")
    content: str = Field(description="内容")
    question_type: Optional[str] = Field(None, description="题型：技术/项目/行为/反问")

class InterviewFeedback(BaseModel):
    """面试反馈"""
    score: float = Field(description="回答得分 0-100")
    highlights: List[str] = Field(default_factory=list, description="答得好的地方")
    improvements: List[str] = Field(default_factory=list, description="需要改进的地方")
    suggested_answer: str = Field(default="", description="参考回答")

# ---------- API 请求/响应 ----------
class AnalyzeRequest(BaseModel):
    """分析请求"""
    resume_text: str = Field(description="简历文本")
    jd_text: Optional[str] = Field(None, description="JD 文本")
    analysis_type: str = Field("full", description="分析类型：resume/match/optimize/interview/full")

class AnalyzeResponse(BaseModel):
    """分析响应"""
    success: bool = True
    message: str = "分析完成"
    data: Optional[Dict[str, Any]] = None
    trace_id: str = ""