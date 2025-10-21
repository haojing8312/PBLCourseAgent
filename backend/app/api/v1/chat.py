"""
Chat API - 课程设计对话端点

提供ChatGPT式的流式对话API
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json
import logging
import re

from app.core.database import get_db
from app.models.course_project import CourseProject
from app.agents.course_chat_agent import get_chat_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


# ========== Request/Response Models ==========


class ConversationMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., description="user | assistant | system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """对话请求"""

    course_id: int = Field(..., description="课程ID")
    message: str = Field(..., min_length=1, description="用户消息")
    current_step: int = Field(default=1, ge=1, le=3, description="当前步骤 (1-3)")
    conversation_history: List[ConversationMessage] = Field(
        default=[], description="对话历史（不包含当前消息）"
    )


# ========== SSE Stream Generator ==========


async def stream_chat_response(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    current_step: int,
    course_info: Dict[str, Any],
    stage_one_data: Optional[str],
    stage_two_data: Optional[str],
    stage_three_data: Optional[str],
):
    """
    生成流式对话响应（SSE格式）- V4版本（支持Artifact事件）

    Args:
        stage_one_data: Stage 1 Markdown字符串
        stage_two_data: Stage 2 Markdown字符串
        stage_three_data: Stage 3 Markdown字符串

    SSE格式：
    data: {"type": "chunk", "content": "文本片段"}\\n\\n
    data: {"type": "artifact", "action": "regenerate", "stage": 1, "instructions": "..."}\\n\\n
    data: {"type": "done"}\\n\\n
    """
    try:
        chat_agent = get_chat_agent()

        # 开始事件
        yield f"data: {json.dumps({'type': 'start'}, ensure_ascii=False)}\n\n"

        # 累积完整的AI回复（用于检测REGENERATE标记）
        full_response = ""

        # 流式输出AI回复
        async for chunk in chat_agent.chat_stream(
            user_message=user_message,
            conversation_history=conversation_history,
            current_step=current_step,
            course_info=course_info,
            stage_one_data=stage_one_data,
            stage_two_data=stage_two_data,
            stage_three_data=stage_three_data,
        ):
            # 累积完整回复
            full_response += chunk

            # 发送文本块
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

        # 检测是否需要重新生成
        # 格式：[REGENERATE:STAGE_X:修改说明]
        regenerate_match = re.match(r'\[REGENERATE:STAGE_(\d+):(.*?)\]', full_response)

        if regenerate_match:
            stage = int(regenerate_match.group(1))
            instructions = regenerate_match.group(2).strip()

            logger.info(f"[ChatAPI] Detected regenerate intent: Stage {stage}, instructions: {instructions}")

            # 发送artifact事件
            artifact_event = {
                'type': 'artifact',
                'action': 'regenerate',
                'stage': stage,
                'instructions': instructions
            }
            yield f"data: {json.dumps(artifact_event, ensure_ascii=False)}\n\n"

        # 完成事件
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    except Exception as e:
        logger.error(f"[ChatAPI] Stream error: {e}", exc_info=True)
        # 发送错误事件
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    流式对话API（SSE）

    对标ChatGPT的流式响应体验

    使用方式：
    ```javascript
    const response = await fetch('/api/v1/chat/stream', {
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
          if (data.type === 'chunk') {
            // 渲染AI回复片段
            console.log(data.content);
          }
        }
      }
    }
    ```
    """
    try:
        # 获取课程信息和数据
        course = db.query(CourseProject).filter(
            CourseProject.id == request.course_id
        ).first()

        if not course:
            raise HTTPException(
                status_code=404,
                detail=f"Course {request.course_id} not found"
            )

        # 准备上下文
        course_info = {
            "title": course.title,
            "subject": course.subject,
            "grade_level": course.grade_level,
            "duration_weeks": course.duration_weeks,
            "description": course.description,
        }

        # 转换对话历史格式
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # 返回流式响应
        return StreamingResponse(
            stream_chat_response(
                user_message=request.message,
                conversation_history=conversation_history,
                current_step=request.current_step,
                course_info=course_info,
                stage_one_data=course.stage_one_data,
                stage_two_data=course.stage_two_data,
                stage_three_data=course.stage_three_data,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ChatAPI] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_non_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    非流式对话API

    返回完整的AI回复（不推荐，建议使用流式）
    """
    try:
        course = db.query(CourseProject).filter(
            CourseProject.id == request.course_id
        ).first()

        if not course:
            raise HTTPException(
                status_code=404,
                detail=f"Course {request.course_id} not found"
            )

        course_info = {
            "title": course.title,
            "subject": course.subject,
            "grade_level": course.grade_level,
            "duration_weeks": course.duration_weeks,
            "description": course.description,
        }

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        chat_agent = get_chat_agent()

        response = await chat_agent.chat_non_stream(
            user_message=request.message,
            conversation_history=conversation_history,
            current_step=request.current_step,
            course_info=course_info,
            stage_one_data=course.stage_one_data,
            stage_two_data=course.stage_two_data,
            stage_three_data=course.stage_three_data,
        )

        return {
            "message": response,
            "course_id": request.course_id,
            "current_step": request.current_step,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ChatAPI] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
