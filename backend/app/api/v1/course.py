"""
V3 API: 课程项目CRUD和对话历史API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.course_project import CourseProject

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


# ========== Request/Response Models ==========


class CourseCreateRequest(BaseModel):
    """创建课程请求"""

    title: str = Field(..., min_length=1, max_length=255)
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, ge=1, le=52)
    description: Optional[str] = None


class CourseUpdateRequest(BaseModel):
    """更新课程基本信息"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, ge=1, le=52)
    description: Optional[str] = None


class StageDataUpdate(BaseModel):
    """更新Stage数据 - Markdown版本"""

    markdown: str = Field(..., description="Stage数据Markdown文本")


class ConversationMessage(BaseModel):
    """对话消息"""

    role: str = Field(..., description="user | assistant | system")
    content: str = Field(..., description="消息内容")
    step: Optional[int] = Field(None, description="所属步骤 (1-3)")


class ConversationAddRequest(BaseModel):
    """添加对话消息请求"""

    messages: List[ConversationMessage] = Field(..., description="消息列表")


class CourseResponse(BaseModel):
    """课程响应 - Markdown版本"""

    id: int
    title: str
    subject: Optional[str]
    grade_level: Optional[str]
    duration_weeks: Optional[int]
    description: Optional[str]
    stage_one_data: Optional[str]  # Markdown字符串
    stage_two_data: Optional[str]  # Markdown字符串
    stage_three_data: Optional[str]  # Markdown字符串
    conversation_history: Optional[List[Dict[str, Any]]]
    stage_one_version: Optional[datetime]
    stage_two_version: Optional[datetime]
    stage_three_version: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== CRUD Endpoints ==========


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(request: CourseCreateRequest, db: Session = Depends(get_db)):
    """
    创建新课程项目
    """
    try:
        course = CourseProject(
            title=request.title,
            subject=request.subject,
            grade_level=request.grade_level,
            duration_weeks=request.duration_weeks,
            description=request.description,
            conversation_history=[],  # 初始化为空列表
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        logger.info(f"Created course: {course.id} - {course.title}")
        return course

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating course: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course: {str(e)}",
        )


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    获取课程详情
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    return course


@router.get("", response_model=List[CourseResponse])
def list_courses(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    获取课程列表
    """
    courses = (
        db.query(CourseProject)
        .order_by(CourseProject.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return courses


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int, request: CourseUpdateRequest, db: Session = Depends(get_db)
):
    """
    更新课程基本信息
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    # 更新字段
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    try:
        db.commit()
        db.refresh(course)
        logger.info(f"Updated course: {course_id}")
        return course

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating course: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update course: {str(e)}",
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    删除课程
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        db.delete(course)
        db.commit()
        logger.info(f"Deleted course: {course_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting course: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete course: {str(e)}",
        )


# ========== Stage Data Endpoints ==========


@router.put("/{course_id}/stage-one", response_model=CourseResponse)
def update_stage_one(
    course_id: int, request: StageDataUpdate, db: Session = Depends(get_db)
):
    """
    更新Stage One数据 (Markdown格式)
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        course.stage_one_data = request.markdown
        course.stage_one_version = datetime.utcnow()
        db.commit()
        db.refresh(course)
        logger.info(f"Updated stage one (Markdown) for course: {course_id}, length: {len(request.markdown)}")
        return course

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stage one: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update stage one: {str(e)}",
        )


@router.put("/{course_id}/stage-two", response_model=CourseResponse)
def update_stage_two(
    course_id: int, request: StageDataUpdate, db: Session = Depends(get_db)
):
    """
    更新Stage Two数据 (Markdown格式)
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        course.stage_two_data = request.markdown
        course.stage_two_version = datetime.utcnow()
        db.commit()
        db.refresh(course)
        logger.info(f"Updated stage two (Markdown) for course: {course_id}, length: {len(request.markdown)}")
        return course

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stage two: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update stage two: {str(e)}",
        )


@router.put("/{course_id}/stage-three", response_model=CourseResponse)
def update_stage_three(
    course_id: int, request: StageDataUpdate, db: Session = Depends(get_db)
):
    """
    更新Stage Three数据 (Markdown格式)
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        course.stage_three_data = request.markdown
        course.stage_three_version = datetime.utcnow()
        db.commit()
        db.refresh(course)
        logger.info(f"Updated stage three (Markdown) for course: {course_id}, length: {len(request.markdown)}")
        return course

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stage three: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update stage three: {str(e)}",
        )


# ========== Export Endpoints ==========


@router.get("/{course_id}/export/markdown")
async def export_course_markdown(course_id: int, db: Session = Depends(get_db)):
    """
    导出课程为Markdown格式

    Returns:
        Markdown文件内容
    """
    from fastapi.responses import Response
    from app.services.export_service import get_export_service

    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        export_service = get_export_service()

        # 准备课程信息
        course_info = {
            "title": course.title,
            "subject": course.subject,
            "grade_level": course.grade_level,
            "duration_weeks": course.duration_weeks,
            "description": course.description,
        }

        # 导出
        filename, markdown_content = export_service.export_for_download(
            stage_one_data=course.stage_one_data,
            stage_two_data=course.stage_two_data,
            stage_three_data=course.stage_three_data,
            course_info=course_info,
        )

        logger.info(f"Exported course {course_id} to Markdown ({len(markdown_content)} bytes)")

        return Response(
            content=markdown_content,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error exporting course: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


# ========== Conversation History Endpoints ==========


@router.post("/{course_id}/conversation", response_model=CourseResponse)
def add_conversation_messages(
    course_id: int, request: ConversationAddRequest, db: Session = Depends(get_db)
):
    """
    添加对话消息到历史记录
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        # 获取现有对话历史
        history = course.conversation_history or []

        # 添加新消息
        for msg in request.messages:
            history.append(
                {
                    "id": f"{datetime.utcnow().timestamp()}_{len(history)}",
                    "role": msg.role,
                    "content": msg.content,
                    "step": msg.step,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        course.conversation_history = history
        db.commit()
        db.refresh(course)

        logger.info(
            f"Added {len(request.messages)} messages to course {course_id} conversation"
        )
        return course

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding conversation messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add messages: {str(e)}",
        )


@router.get("/{course_id}/conversation")
def get_conversation_history(
    course_id: int, step: Optional[int] = None, db: Session = Depends(get_db)
):
    """
    获取对话历史
    可选过滤特定步骤的对话
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    history = course.conversation_history or []

    # 过滤特定步骤
    if step is not None:
        history = [msg for msg in history if msg.get("step") == step]

    return {"course_id": course_id, "messages": history}


@router.delete("/{course_id}/conversation", status_code=status.HTTP_204_NO_CONTENT)
def clear_conversation_history(
    course_id: int, step: Optional[int] = None, db: Session = Depends(get_db)
):
    """
    清除对话历史
    如果指定step，则只清除该步骤的对话
    """
    course = db.query(CourseProject).filter(CourseProject.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Course {course_id} not found"
        )

    try:
        if step is None:
            # 清除所有对话
            course.conversation_history = []
        else:
            # 只清除特定步骤
            history = course.conversation_history or []
            course.conversation_history = [msg for msg in history if msg.get("step") != step]

        db.commit()
        logger.info(f"Cleared conversation for course {course_id}, step: {step}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation: {str(e)}",
        )
