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