"""LangGraph 工作流编排"""
import uuid
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from app.agents.resume_parser import ResumeParserAgent
from app.agents.jd_matcher import JDMatcherAgent
from app.agents.resume_optimizer import ResumeOptimizerAgent
from app.models.schemas import ParsedResume, MatchResult, ResumeOptimization


# ---------- 工作流状态 ----------
class AgentState(TypedDict):
    """工作流状态"""
    trace_id: str
    resume_text: str
    jd_text: str
    analysis_type: str  # resume / match / optimize / full

    parsed_resume: ParsedResume | None
    match_result: MatchResult | None
    optimization_result: ResumeOptimization | None

    error: str | None


# ---------- 节点函数 ----------
def parse_resume(state: AgentState) -> AgentState:
    """节点：简历解析"""
    agent = ResumeParserAgent()
    result = agent.run(state["resume_text"], state["trace_id"])
    state["parsed_resume"] = result
    return state


def match_jd(state: AgentState) -> AgentState:
    """节点：JD 匹配"""
    if not state["jd_text"]:
        return state
    agent = JDMatcherAgent()
    result = agent.run(state["parsed_resume"], state["jd_text"], state["trace_id"])
    state["match_result"] = result
    return state


def optimize_resume(state: AgentState) -> AgentState:
    """节点：简历优化"""
    agent = ResumeOptimizerAgent()
    target = state.get("match_result", None)
    target_pos = state["parsed_resume"].target_position if state["parsed_resume"] else ""
    result = agent.run(state["parsed_resume"], target_pos, state["trace_id"])
    state["optimization_result"] = result
    return state


def route_after_parse(state: AgentState) -> str:
    """条件路由：解析完简历后走哪条路"""
    atype = state["analysis_type"]
    if atype == "resume":
        return END
    elif atype == "match":
        return "match_jd"
    else:  # full / optimize
        return "match_jd" if state["jd_text"] else "optimize_resume"


def route_after_match(state: AgentState) -> str:
    """条件路由：匹配后要不要继续优化"""
    atype = state["analysis_type"]
    if atype in ("full", "optimize"):
        return "optimize_resume"
    return END


# ---------- 构建工作流 ----------
def build_workflow():
    """构建 LangGraph 工作流"""
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("parse_resume", parse_resume)
    workflow.add_node("match_jd", match_jd)
    workflow.add_node("optimize_resume", optimize_resume)

    # 入口
    workflow.set_entry_point("parse_resume")

    # 条件边：解析完简历后路由
    workflow.add_conditional_edges(
        "parse_resume",
        route_after_parse,
        {
            "match_jd": "match_jd",
            "optimize_resume": "optimize_resume",
            END: END,
        }
    )

    # 匹配完后路由
    workflow.add_conditional_edges(
        "match_jd",
        route_after_match,
        {
            "optimize_resume": "optimize_resume",
            END: END,
        }
    )

    # 优化完结束
    workflow.add_edge("optimize_resume", END)

    return workflow.compile()


# 全局工作流实例
job_workflow = build_workflow()


def run_analysis(
        resume_text: str,
        jd_text: str = None,
        analysis_type: str = "full",
) -> dict:
    """运行完整分析流程"""
    trace_id = str(uuid.uuid4())[:8]

    initial_state = AgentState(
        trace_id=trace_id,
        resume_text=resume_text,
        jd_text=jd_text or "",
        analysis_type=analysis_type,
        parsed_resume=None,
        match_result=None,
        optimization_result=None,
        error=None,
    )

    result = job_workflow.invoke(initial_state)
    return result