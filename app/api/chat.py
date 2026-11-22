"""求职分析接口"""
import uuid
from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.workflow.graph import run_analysis
from app.governance.rate_limiter import rate_limiter

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, req: Request):
    """求职分析（简历解析 + JD 匹配 + 优化建议）"""
    trace_id = str(uuid.uuid4())[:8]

    # 限流检查
    client_ip = req.client.host if req.client else "unknown"
    if not rate_limiter.check(f"analyze:{client_ip}"):
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请 {rate_limiter.window_seconds} 秒后再试"
        )

    try:
        result = run_analysis(
            resume_text=request.resume_text,
            jd_text=request.jd_text,
            analysis_type=request.analysis_type,
        )

        # 组装返回数据
        data = {}
        if result.get("parsed_resume"):
            data["resume"] = result["parsed_resume"].model_dump()
        if result.get("match_result"):
            data["match"] = result["match_result"].model_dump()
        if result.get("optimization_result"):
            data["optimization"] = result["optimization_result"].model_dump()

        return AnalyzeResponse(
            success=True,
            message="分析完成",
            data=data,
            trace_id=trace_id,
        )

    except Exception as e:
        return AnalyzeResponse(
            success=False,
            message=f"分析失败：{str(e)}",
            trace_id=trace_id,
        )


@router.get("/governance/status")
async def governance_status():
    """治理状态查询（限流器、熔断器状态）"""
    from app.governance.circuit_breaker import llm_circuit_breaker

    return {
        "rate_limiter": {
            "max_requests": rate_limiter.max_requests,
            "window_seconds": rate_limiter.window_seconds,
        },
        "circuit_breaker": {
            "state": llm_circuit_breaker.state.value,
            "failure_count": llm_circuit_breaker._failure_count,
            "failure_threshold": llm_circuit_breaker.failure_threshold,
        }
    }