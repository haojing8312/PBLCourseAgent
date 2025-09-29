"""
Agent 2: 评估框架设计 (Assessment Framework Agent)
"""
import json
import time
from typing import Dict, Any
from app.core.openai_client import openai_client
from app.core.config import settings


class AssessmentFrameworkAgent:
    """评估框架设计Agent"""

    def __init__(self):
        self.agent_name = "Genesis Two"
        self.timeout = settings.agent2_timeout

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """
# ROLE & CONTEXT
You are "Genesis Two", a meticulous curriculum evaluator with expertise in educational assessment and PBL evaluation frameworks. Your task is to create a comprehensive assessment framework based on the provided project foundation. The framework must be practical for a non-expert teacher to use.

# INSTRUCTION
Based on the project foundation JSON, generate an assessment framework. The output MUST be a valid JSON object following the specified schema. The rubric descriptions should be clear, positive, and action-oriented.

# SCHEMA
{
  "summativeRubric": [
    {
      "dimension": "The skill or quality being measured (e.g., '创意构思').",
      "level_1_desc": "Description for '新手' level.",
      "level_2_desc": "Description for '学徒' level.",
      "level_3_desc": "Description for '工匠' level.",
      "level_4_desc": "Description for '大师' level."
    }
  ],
  "formativeCheckpoints": [
    {
      "name": "The name of the checkpoint (e.g., '创意概念审核').",
      "triggerTime": "When this check happens (e.g., '上午结束前').",
      "purpose": "What the teacher should check for."
    }
  ]
}

# GUIDELINES FOR RUBRIC CREATION
- Create 3-4 rubric dimensions that cover both technical skills and soft skills
- Each dimension should have 4 levels: 新手, 学徒, 工匠, 大师
- Descriptions should be specific and observable behaviors
- Focus on what students CAN do at each level, not what they lack
- Include technical AI tool usage and creative/collaboration skills
- Make descriptions age-appropriate for the target audience

# GUIDELINES FOR CHECKPOINTS
- Create 2-4 formative checkpoints throughout the project timeline
- Checkpoints should be at logical stopping points in the workflow
- Each checkpoint should have a clear purpose for quality assurance
- Include specific timing that makes sense for the project duration
- Focus on preventing problems rather than just catching them

# OUTPUT REQUIREMENTS
- All text must be in Chinese
- Rubric dimensions should align with the learning objectives from the project foundation
- Checkpoints should align with the anticipated workflow and timeline
- Descriptions should be clear enough for a non-expert teacher to apply consistently
"""

    def _build_user_prompt(self, foundation_data: Dict[str, Any]) -> str:
        """构建用户提示词"""
        return f"""
# PROJECT FOUNDATION
{json.dumps(foundation_data, ensure_ascii=False, indent=2)}

请基于以上项目基础信息，生成符合Schema要求的评估框架JSON。确保：
1. 总结性量规（summativeRubric）涵盖学习目标中的硬技能和软技能
2. 每个维度的4个等级描述具体、可观测、积极正面
3. 形成性检查点（formativeCheckpoints）在关键节点设置，有明确的质量保证目的
4. 评估标准适合目标年龄段，便于非专业教师操作

直接返回JSON格式，不要任何额外说明。
"""

    async def generate(self, foundation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成评估框架

        Args:
            foundation_data: Agent 1的输出数据

        Returns:
            包含生成结果和元数据的字典
        """
        start_time = time.time()

        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(foundation_data)

            # 调用OpenAI API
            model = settings.agent2_model or settings.openai_model
            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=2500,
                temperature=0.6,
                timeout=self.timeout
            )

            end_time = time.time()
            response_time = end_time - start_time

            if not response["success"]:
                return {
                    "success": False,
                    "error": response.get("error", "Unknown error"),
                    "response_time": response_time,
                    "agent": "assessment_framework"
                }

            # 尝试解析JSON响应
            try:
                content = response["content"].strip()
                # 如果响应包含代码块，提取JSON部分
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                assessment_data = json.loads(content)

                return {
                    "success": True,
                    "data": assessment_data,
                    "response_time": response_time,
                    "token_usage": response["token_usage"],
                    "agent": "assessment_framework"
                }

            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": response["content"],
                    "response_time": response_time,
                    "agent": "assessment_framework"
                }

        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time": end_time - start_time,
                "agent": "assessment_framework"
            }