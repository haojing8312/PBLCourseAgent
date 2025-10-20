"""
Data models package
"""
from app.models.schemas import (
    ProjectInput,
    ProjectFoundation,
    AssessmentFramework,
    LearningBlueprint,
    GenerationResult,
    ApiResponse,
    HealthCheck,
    ChatMessage,
    ChatRequest,
    Stage1Input,
    Stage1Output,
    Stage2Input,
    Stage2Output,
    Stage3Input,
    Stage3Output,
)
from app.models.course_project import CourseProject

# V3 UbD Data Models
from app.models.stage_data import (
    # Stage One
    StageOneData,
    GoalItem,
    UnderstandingItem,
    QuestionItem,
    KnowledgeItem,
    SkillItem,
    # Stage Two
    StageTwoData,
    PerformanceTask,
    Rubric,
    RubricDimension,
    RubricLevel,
    OtherEvidence,
    # Stage Three
    StageThreeData,
    PBLPhase,
    Activity,
    # Workflow
    WorkflowRequest,
    WorkflowResponse,
)

__all__ = [
    # Legacy schemas
    "ProjectInput",
    "ProjectFoundation",
    "AssessmentFramework",
    "LearningBlueprint",
    "GenerationResult",
    "ApiResponse",
    "HealthCheck",
    "ChatMessage",
    "ChatRequest",
    "Stage1Input",
    "Stage1Output",
    "Stage2Input",
    "Stage2Output",
    "Stage3Input",
    "Stage3Output",
    # ORM
    "CourseProject",
    # V3 Stage Models
    "StageOneData",
    "GoalItem",
    "UnderstandingItem",
    "QuestionItem",
    "KnowledgeItem",
    "SkillItem",
    "StageTwoData",
    "PerformanceTask",
    "Rubric",
    "RubricDimension",
    "RubricLevel",
    "OtherEvidence",
    "StageThreeData",
    "PBLPhase",
    "Activity",
    "WorkflowRequest",
    "WorkflowResponse",
]
