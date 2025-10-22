"""
V3 API: 工作流生成端点 (Server-Sent Events)
支持流式生成三个UbD阶段，带进度事件 - 集成真实的Agent V3
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["workflow"])


# ========== Request/Response Models ==========


class WorkflowRequest(BaseModel):
    """工作流请求"""

    # 课程基本信息
    title: str = Field(..., description="课程名称")
    subject: Optional[str] = Field(None, description="学科领域")
    grade_level: Optional[str] = Field(None, description="年级水平")

    # 课程时长 - 灵活方案
    total_class_hours: Optional[int] = Field(None, ge=1, description="总课时数（按45分钟标准课时）")
    schedule_description: Optional[str] = Field(None, description="上课周期描述，例如：共4周，每周1次，一次半天3个小时")

    description: Optional[str] = Field(None, description="课程简介")

    # 生成控制
    stages_to_generate: List[int] = Field(
        default=[1, 2, 3], description="需要生成的阶段 (1, 2, 3)"
    )

    # Stage数据（如果用户修改过，重新生成时提供） - Markdown格式
    stage_one_data: Optional[str] = Field(
        None, description="Stage One Markdown数据（修改后重新生成时提供）"
    )
    stage_two_data: Optional[str] = Field(
        None, description="Stage Two Markdown数据（修改后重新生成时提供）"
    )


# ========== SSE Stream Generator ==========


async def stream_workflow_events(request: WorkflowRequest):
    """
    生成工作流SSE事件流 - 使用真实的WorkflowServiceV3

    事件格式:
    data: {"event": "...", "data": {...}}

    事件类型:
    - start: 开始生成
    - progress: 进度更新 (stage, progress, message)
    - stage_complete: 阶段完成 (stage, result, validation, generation_time)
    - error: 错误 (message, stage)
    - complete: 全部完成
    """
    from app.services.workflow_service_v3 import get_workflow_service_v3

    try:
        workflow_service = get_workflow_service_v3()

        # 使用真实的workflow service进行流式生成
        async for sse_event in workflow_service.stream_workflow(
            title=request.title,
            subject=request.subject or "",
            grade_level=request.grade_level or "",
            total_class_hours=request.total_class_hours,
            schedule_description=request.schedule_description or "",
            description=request.description or "",
            stages_to_generate=request.stages_to_generate,
            stage_one_data=request.stage_one_data,
            stage_two_data=request.stage_two_data,
        ):
            yield sse_event

    except Exception as e:
        logger.error(f"Workflow generation error: {e}", exc_info=True)
        # 格式化错误事件
        yield f"data: {json.dumps({'event': 'error', 'data': {'message': str(e), 'stage': None}}, ensure_ascii=False)}\n\n"


def format_sse_event(event_data: dict) -> str:
    """
    格式化SSE事件

    SSE格式：
    data: {"event": "...", "data": {...}}\\n\\n
    """
    return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"


@router.post("/workflow/stream")
async def stream_workflow(request: WorkflowRequest):
    """
    流式生成完整工作流

    Server-Sent Events (SSE) endpoint
    客户端使用EventSource连接或fetch with stream

    事件类型:
    - start: 开始生成
    - progress: 进度更新 (stage, progress, message)
    - stage_complete: 阶段完成 (stage, result)
    - error: 错误 (message, stage)
    - complete: 全部完成

    示例 (fetch with stream):
    ```javascript
    const response = await fetch('/api/v1/workflow/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\\n\\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          console.log(data.event, data.data);
        }
      }
    }
    ```
    """
    try:
        return StreamingResponse(
            stream_workflow_events(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
                "Access-Control-Allow-Origin": "*",  # CORS
            },
        )
    except Exception as e:
        logger.error(f"Stream workflow endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========== 健康检查 ==========


@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {
        "status": "healthy",
        "api_version": "v1",
        "service": "UbD-PBL Course Architect V3",
        "endpoints": {
            "workflow_stream": "/api/v1/workflow/stream",
        },
    }
