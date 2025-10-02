"""
数据模型定义
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectInput(BaseModel):
    """项目输入数据"""
    course_topic: str = Field(..., description="课程主题")
    course_overview: str = Field(..., description="课程概要")
    age_group: str = Field(..., description="年龄段")
    duration: str = Field(..., description="课程时长")
    ai_tools: str = Field(..., description="核心AI工具/技能")


class ProjectFoundation(BaseModel):
    """项目基础定义输出"""
    driving_question: str = Field(..., description="驱动性问题")
    final_deliverable: str = Field(..., description="最终公开成果")
    cover_page: Dict[str, Any] = Field(..., description="封面页信息")
    created_at: datetime = Field(default_factory=datetime.now)


class AssessmentFramework(BaseModel):
    """评估框架输出"""
    rubric: Dict[str, Any] = Field(..., description="评估量规")
    assessment_criteria: List[Dict[str, Any]] = Field(..., description="评估标准")
    created_at: datetime = Field(default_factory=datetime.now)


class LearningBlueprint(BaseModel):
    """学习蓝图输出"""
    day_by_day_plan: Dict[str, Any] = Field(..., description="逐日教学计划")
    activities: List[Dict[str, Any]] = Field(..., description="活动详情")
    materials: List[str] = Field(..., description="所需材料")
    created_at: datetime = Field(default_factory=datetime.now)


class GenerationResult(BaseModel):
    """完整生成结果"""
    project_foundation: ProjectFoundation
    assessment_framework: AssessmentFramework
    learning_blueprint: LearningBlueprint
    total_time: float = Field(..., description="总生成时间（秒）")
    agent_times: Dict[str, float] = Field(..., description="各Agent耗时")
    quality_score: Optional[float] = Field(None, description="质量得分")


class ApiResponse(BaseModel):
    """API统一响应格式"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthCheck(BaseModel):
    """健康检查响应"""
    status: str = Field("healthy", description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field("1.0.0", description="API版本")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息角色: user/assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    context: Optional[str] = Field(None, description="对话上下文")
    session_id: Optional[str] = Field(None, description="会话ID")


# ========== 分阶段生成的新Schema ==========

class Stage1Input(BaseModel):
    """阶段1输入 - 项目基础定义"""
    course_topic: str = Field(..., description="课程主题")
    course_overview: str = Field(..., description="课程概要")
    age_group: str = Field(..., description="年龄段")
    duration: str = Field(..., description="课程时长")
    ai_tools: str = Field(..., description="核心AI工具/技能")


class Stage1Output(BaseModel):
    """阶段1输出 - 项目基础定义"""
    driving_question: str = Field(..., description="驱动性问题")
    project_definition: str = Field(..., description="项目定义")
    final_deliverable: str = Field(..., description="最终公开成果")
    cover_page: str = Field(..., description="封面页信息（Markdown格式）")
    raw_content: str = Field(..., description="原始AI生成内容")
    generation_time: float = Field(..., description="生成耗时（秒）")


class Stage2Input(BaseModel):
    """阶段2输入 - 评估框架设计"""
    # 来自阶段1的输出（可能被用户修改）
    driving_question: str = Field(..., description="驱动性问题")
    project_definition: str = Field(..., description="项目定义")
    final_deliverable: str = Field(..., description="最终公开成果")
    # 原始课程信息
    course_topic: str = Field(..., description="课程主题")
    age_group: str = Field(..., description="年龄段")
    duration: str = Field(..., description="课程时长")


class Stage2Output(BaseModel):
    """阶段2输出 - 评估框架"""
    rubric_markdown: str = Field(..., description="评估量规（Markdown格式）")
    evaluation_criteria: str = Field(..., description="评估标准")
    raw_content: str = Field(..., description="原始AI生成内容")
    generation_time: float = Field(..., description="生成耗时（秒）")


class Stage3Input(BaseModel):
    """阶段3输入 - 学习蓝图生成"""
    # 来自阶段1
    driving_question: str = Field(..., description="驱动性问题")
    project_definition: str = Field(..., description="项目定义")
    final_deliverable: str = Field(..., description="最终公开成果")
    # 来自阶段2（可能被用户修改）
    rubric_markdown: str = Field(..., description="评估量规")
    evaluation_criteria: str = Field(..., description="评估标准")
    # 原始课程信息
    course_topic: str = Field(..., description="课程主题")
    age_group: str = Field(..., description="年龄段")
    duration: str = Field(..., description="课程时长")
    ai_tools: str = Field(..., description="核心AI工具/技能")


class Stage3Output(BaseModel):
    """阶段3输出 - 学习蓝图"""
    day_by_day_plan: str = Field(..., description="逐日教学计划（Markdown格式）")
    activities_summary: str = Field(..., description="活动总结")
    materials_list: str = Field(..., description="所需材料清单")
    raw_content: str = Field(..., description="原始AI生成内容")
    generation_time: float = Field(..., description="生成耗时（秒）")