"""
AI Agents Package
UbD-PBL Course Architect Agents
"""

# V3 Agents (UbD Framework)
from app.agents.project_foundation_v3 import ProjectFoundationAgentV3
from app.agents.assessment_framework_v3 import AssessmentFrameworkAgentV3
from app.agents.learning_blueprint_v3 import LearningBlueprintAgentV3

# V1 Agents (legacy, for backwards compatibility)
try:
    from app.agents.project_foundation_agent import ProjectFoundationAgent
    from app.agents.assessment_framework_agent import AssessmentFrameworkAgent
    from app.agents.learning_blueprint_agent import LearningBlueprintAgent
except ImportError:
    # V1 agents may not exist in fresh setup
    ProjectFoundationAgent = None
    AssessmentFrameworkAgent = None
    LearningBlueprintAgent = None

__all__ = [
    # V3 (recommended)
    "ProjectFoundationAgentV3",
    "AssessmentFrameworkAgentV3",
    "LearningBlueprintAgentV3",
    # V1 (legacy)
    "ProjectFoundationAgent",
    "AssessmentFrameworkAgent",
    "LearningBlueprintAgent",
]
