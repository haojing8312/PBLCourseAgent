"""
V3 API: 工作流生成端点 (Server-Sent Events)
支持流式生成三个UbD阶段，带进度事件
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["workflow"])


# ========== Request/Response Models ==========


class WorkflowRequest(BaseModel):
    """
    工作流请求
    """

    # 课程基本信息
    title: str = Field(..., description="课程名称")
    subject: Optional[str] = Field(None, description="学科领域")
    grade_level: Optional[str] = Field(None, description="年级水平")
    duration_weeks: int = Field(..., description="课程时长（周）", ge=1, le=52)
    description: Optional[str] = Field(None, description="课程简介")

    # 生成控制
    stages_to_generate: List[int] = Field(
        default=[1, 2, 3], description="需要生成的阶段 (1, 2, 3)"
    )

    # Stage数据（如果用户修改过）
    stage_one_data: Optional[Dict[str, Any]] = Field(
        None, description="Stage One数据（修改后重新生成时提供）"
    )
    stage_two_data: Optional[Dict[str, Any]] = Field(
        None, description="Stage Two数据（修改后重新生成时提供）"
    )


class SSEEvent(BaseModel):
    """
    SSE事件基类
    """

    event: str = Field(..., description="事件类型")
    data: Dict[str, Any] = Field(..., description="事件数据")


# ========== SSE事件类型 ==========
# - progress: 进度更新 {"stage": 1, "progress": 50, "message": "生成中..."}
# - stage_complete: 阶段完成 {"stage": 1, "data": {...}}
# - error: 错误 {"message": "...", "stage": 1}
# - complete: 全部完成 {}


async def stream_workflow_events(request: WorkflowRequest):
    """
    生成工作流SSE事件流

    事件格式:
    data: {"event": "progress", "data": {...}}
    data: {"event": "stage_complete", "data": {...}}
    data: {"event": "error", "data": {...}}
    data: {"event": "complete", "data": {...}}
    """
    try:
        # 发送开始事件
        yield format_sse_event(
            {
                "event": "start",
                "data": {
                    "message": "开始生成UbD-PBL课程方案",
                    "stages": request.stages_to_generate,
                },
            }
        )

        # 为了演示，这里使用模拟生成
        # 实际应该调用真实的Agent服务
        # TODO: 在 Phase 3 中集成真实的Agent

        # Stage 1: 确定预期学习结果 (G/U/Q/K/S)
        if 1 in request.stages_to_generate:
            yield format_sse_event(
                {
                    "event": "progress",
                    "data": {
                        "stage": 1,
                        "progress": 0,
                        "message": "阶段1：正在分析课程目标...",
                    },
                }
            )

            await asyncio.sleep(0.5)  # 模拟生成

            # 模拟进度更新
            for progress in [25, 50, 75]:
                yield format_sse_event(
                    {
                        "event": "progress",
                        "data": {
                            "stage": 1,
                            "progress": progress,
                            "message": f"阶段1：生成G/U/Q/K/S框架... {progress}%",
                        },
                    }
                )
                await asyncio.sleep(0.3)

            # Stage 1 完成
            stage_one_data = {
                "goals": [
                    {
                        "text": "学生将能够自主地设计AI解决方案来解决真实问题",
                        "order": 0,
                    }
                ],
                "understandings": [
                    {
                        "text": "理解AI技术的双刃剑特性",
                        "order": 0,
                        "rationale": "这是一个永恒的技术哲学洞察",
                        "validation_score": 0.85,
                    }
                ],
                "questions": [{"text": "AI技术应该在多大程度上参与人类决策？", "order": 0}],
                "knowledge": [{"text": "Python基本语法", "order": 0}],
                "skills": [{"text": "使用Python编写代码", "order": 0}],
            }

            yield format_sse_event(
                {
                    "event": "stage_complete",
                    "data": {"stage": 1, "result": stage_one_data},
                }
            )

        # Stage 2: 确定可接受的证据
        if 2 in request.stages_to_generate:
            yield format_sse_event(
                {
                    "event": "progress",
                    "data": {
                        "stage": 2,
                        "progress": 0,
                        "message": "阶段2：正在设计驱动性问题...",
                    },
                }
            )

            await asyncio.sleep(0.5)

            for progress in [30, 60, 90]:
                yield format_sse_event(
                    {
                        "event": "progress",
                        "data": {
                            "stage": 2,
                            "progress": progress,
                            "message": f"阶段2：生成表现性任务和评估量规... {progress}%",
                        },
                    }
                )
                await asyncio.sleep(0.3)

            # Stage 2 完成
            stage_two_data = {
                "driving_question": "我们如何利用AI技术解决社区问题？",
                "driving_question_context": "学生将扮演社区技术顾问...",
                "performance_tasks": [
                    {
                        "title": "任务1: 社区问题调研",
                        "description": "调研社区问题并提出AI解决方案",
                        "milestone_week": 3,
                        "order": 0,
                    }
                ],
                "other_evidence": [],
            }

            yield format_sse_event(
                {
                    "event": "stage_complete",
                    "data": {"stage": 2, "result": stage_two_data},
                }
            )

        # Stage 3: 规划学习体验
        if 3 in request.stages_to_generate:
            yield format_sse_event(
                {
                    "event": "progress",
                    "data": {
                        "stage": 3,
                        "progress": 0,
                        "message": "阶段3：正在规划PBL学习蓝图...",
                    },
                }
            )

            await asyncio.sleep(0.5)

            for progress in [20, 40, 60, 80]:
                yield format_sse_event(
                    {
                        "event": "progress",
                        "data": {
                            "stage": 3,
                            "progress": progress,
                            "message": f"阶段3：生成4阶段PBL活动... {progress}%",
                        },
                    }
                )
                await asyncio.sleep(0.3)

            # Stage 3 完成
            stage_three_data = {
                "pbl_phases": [
                    {
                        "phase_type": "launch",
                        "phase_name": "项目启动",
                        "duration_weeks": 2,
                        "order": 0,
                        "activities": [],
                    }
                ]
            }

            yield format_sse_event(
                {
                    "event": "stage_complete",
                    "data": {"stage": 3, "result": stage_three_data},
                }
            )

        # 全部完成
        yield format_sse_event({"event": "complete", "data": {"message": "课程方案生成完成"}})

    except Exception as e:
        logger.error(f"Workflow generation error: {e}", exc_info=True)
        yield format_sse_event(
            {
                "event": "error",
                "data": {"message": str(e), "stage": None},
            }
        )


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
    客户端使用EventSource连接

    事件类型:
    - start: 开始生成
    - progress: 进度更新 (stage, progress, message)
    - stage_complete: 阶段完成 (stage, result)
    - error: 错误 (message, stage)
    - complete: 全部完成

    示例:
    ```javascript
    const eventSource = new EventSource('/api/v1/workflow/stream', {
      method: 'POST',
      body: JSON.stringify(request)
    });

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'progress') {
        console.log(data.data.message);
      }
    };
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
        "endpoints": {
            "workflow_stream": "/api/v1/workflow/stream",
        },
    }
