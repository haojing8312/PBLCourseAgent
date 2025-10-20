"""
UbD V3 Stage数据模型
定义三个UbD阶段的数据结构（Pydantic）
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ========== Stage One: 确定预期学习结果 (G/U/Q/K/S) ==========


class GoalItem(BaseModel):
    """迁移目标 (G)"""

    text: str = Field(..., description="目标描述：学生将能够自主地...")
    order: int = Field(..., description="顺序")


class UnderstandingItem(BaseModel):
    """持续理解 (U)"""

    text: str = Field(..., description="理解陈述：抽象的big idea")
    order: int = Field(..., description="顺序")
    rationale: str = Field(..., description="为什么这是持续理解")
    validation_score: Optional[float] = Field(
        None, description="语义验证分数 (0-1)", ge=0.0, le=1.0
    )


class QuestionItem(BaseModel):
    """基本问题 (Q)"""

    text: str = Field(..., description="开放性的探究问题")
    order: int = Field(..., description="顺序")


class KnowledgeItem(BaseModel):
    """应掌握知识 (K)"""

    text: str = Field(..., description="具体知识点")
    order: int = Field(..., description="顺序")


class SkillItem(BaseModel):
    """应形成技能 (S)"""

    text: str = Field(..., description="具体技能")
    order: int = Field(..., description="顺序")


class StageOneData(BaseModel):
    """Stage One 完整数据"""

    goals: List[GoalItem] = Field(default_factory=list)
    understandings: List[UnderstandingItem] = Field(default_factory=list)
    questions: List[QuestionItem] = Field(default_factory=list)
    knowledge: List[KnowledgeItem] = Field(default_factory=list)
    skills: List[SkillItem] = Field(default_factory=list)


# ========== Stage Two: 确定可接受的证据 ==========


class RubricLevel(BaseModel):
    """评估量规等级"""

    level: int = Field(..., description="等级 (1-4)", ge=1, le=4)
    label: str = Field(..., description="等级标签：卓越/熟练/发展中/初步")
    description: str = Field(..., description="该等级的具体描述")


class RubricDimension(BaseModel):
    """评估量规维度"""

    name: str = Field(..., description="维度名称")
    weight: float = Field(..., description="权重 (0-1)", ge=0.0, le=1.0)
    levels: List[RubricLevel] = Field(..., description="4个等级")


class Rubric(BaseModel):
    """完整的评估量规"""

    name: str = Field(..., description="量规名称")
    dimensions: List[RubricDimension] = Field(..., description="评估维度列表")


class PerformanceTask(BaseModel):
    """表现性任务"""

    title: str = Field(..., description="任务标题")
    description: str = Field(..., description="任务详细描述")
    context: str = Field(..., description="真实情境说明")
    student_role: str = Field(..., description="学生角色")
    deliverable: str = Field(..., description="最终产出物")
    milestone_week: int = Field(..., description="里程碑周次", ge=1)
    order: int = Field(..., description="任务顺序")
    linked_ubd_elements: Dict[str, List[int]] = Field(
        ...,
        description="关联的UbD元素 {u: [0,1], s: [0,2], k: [1,3]}",
    )
    rubric: Rubric = Field(..., description="评估量规")


class OtherEvidence(BaseModel):
    """其他评估证据"""

    type: str = Field(..., description="证据类型")
    description: str = Field(..., description="描述")


class StageTwoData(BaseModel):
    """Stage Two 完整数据"""

    driving_question: str = Field(..., description="核心驱动性问题")
    driving_question_context: str = Field(..., description="问题的真实情境描述")
    performance_tasks: List[PerformanceTask] = Field(default_factory=list)
    other_evidence: List[OtherEvidence] = Field(default_factory=list)


# ========== Stage Three: 规划学习体验 ==========


class Activity(BaseModel):
    """学习活动"""

    week: int = Field(..., description="所属周次", ge=1)
    title: str = Field(..., description="活动标题")
    description: str = Field(..., description="活动详细描述")
    duration_hours: float = Field(..., description="活动时长（小时）", ge=0.5)
    whereto_labels: List[str] = Field(
        ..., description="WHERETO原则标签 (W/H/E/R/E/T/O)"
    )
    linked_ubd_elements: Dict[str, List[int]] = Field(
        ..., description="关联的UbD元素 {u: [0,1], s: [0,2], k: [1,3]}"
    )
    notes: str = Field(..., description="教学提示和注意事项")


class PBLPhase(BaseModel):
    """PBL阶段"""

    phase_type: str = Field(
        ..., description="阶段类型: launch/build/develop/present"
    )
    phase_name: str = Field(..., description="阶段名称")
    duration_weeks: int = Field(..., description="阶段时长（周）", ge=1)
    order: int = Field(..., description="阶段顺序 (0-3)")
    activities: List[Activity] = Field(default_factory=list)


class StageThreeData(BaseModel):
    """Stage Three 完整数据"""

    pbl_phases: List[PBLPhase] = Field(default_factory=list)


# ========== API请求/响应模型 ==========


class WorkflowRequest(BaseModel):
    """完整工作流请求"""

    title: str = Field(..., description="课程名称")
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    duration_weeks: int = Field(..., ge=1, le=52)
    description: Optional[str] = None


class WorkflowResponse(BaseModel):
    """完整工作流响应"""

    success: bool
    message: str
    stage_one: Optional[StageOneData] = None
    stage_two: Optional[StageTwoData] = None
    stage_three: Optional[StageThreeData] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None
