"""
课程项目数据模型 - SQLAlchemy ORM
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class CourseProject(Base):
    """
    课程项目模型
    存储完整的UbD-PBL课程设计项目
    """
    __tablename__ = "course_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    subject = Column(String(100), nullable=True)
    grade_level = Column(String(100), nullable=True)
    duration_weeks = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

    # UbD Stage One: 确定预期学习结果 (G/U/Q/K/S) - Markdown格式
    stage_one_data = Column(Text, nullable=True, comment="Stage One Markdown: Goals, Understandings, Questions, Knowledge, Skills")

    # UbD Stage Two: 确定可接受的证据 (驱动性问题 + 表现性任务 + 评估量规) - Markdown格式
    stage_two_data = Column(Text, nullable=True, comment="Stage Two Markdown: Driving Question, Performance Tasks, Rubrics")

    # UbD Stage Three: 规划学习体验 (PBL 4阶段 + WHERETO) - Markdown格式
    stage_three_data = Column(Text, nullable=True, comment="Stage Three Markdown: PBL Phases with Activities")

    # 对话历史记录 - 用于User Story 3 (会话持久化)
    conversation_history = Column(
        JSON,
        nullable=True,
        default=list,
        comment="Chat conversation history for each stage"
    )

    # 版本控制字段 - 用于变更检测
    stage_one_version = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    stage_two_version = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    stage_three_version = Column(DateTime(timezone=True), nullable=True, server_default=func.now())

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<CourseProject(id={self.id}, title='{self.title}')>"
