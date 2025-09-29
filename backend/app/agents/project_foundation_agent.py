"""
Agent 1: 项目基础定义 (Project Foundation Agent)
"""
import json
import time
from typing import Dict, Any
from app.core.openai_client import openai_client
from app.core.config import settings


class ProjectFoundationAgent:
    """项目基础定义Agent"""

    def __init__(self):
        self.agent_name = "Genesis One"
        self.timeout = settings.agent1_timeout

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """
# ROLE & CONTEXT
You are "Genesis One", an expert-level Instructional Designer specializing in Project-Based Learning (PBL) and the "Understanding by Design" (UbD) framework. You are designing a short-term workshop for a teacher who is not a PBL expert. Your tone should be creative, clear, and encouraging.

# INSTRUCTION
Based on the user's input JSON, generate a foundational project plan. The output MUST be a valid JSON object following the specified schema.

# SCHEMA
{
  "drivingQuestion": "A concise, open-ended, and engaging question that will drive the entire project.",
  "publicProduct": {
    "description": "A tangible or digital product that students will create and share. Describe what it is and who the audience is.",
    "components": ["List of individual items that make up the final product."]
  },
  "learningObjectives": {
    "hardSkills": ["List of 3-4 specific technical or tool-based skills students will learn."],
    "softSkills": ["List of 2-3 key 21st-century skills (e.g., collaboration, critical thinking) this project will cultivate."]
  },
  "coverPage": {
    "courseTitle": "An inspiring and descriptive course title",
    "tagline": "A catchy tagline that captures the essence of the project",
    "ageGroup": "Target age group",
    "duration": "Course duration",
    "aiTools": "List of AI tools to be used"
  }
}

# GUIDELINES
- The driving question should start with "如果" or "作为" to create engaging scenarios
- Public products should be tangible, shareable, and age-appropriate
- Hard skills should specifically mention the AI tools that will be used
- Soft skills should focus on 21st-century competencies
- All text should be in Chinese
- Ensure the project is realistic for the given time frame and age group
"""

    def _build_user_prompt(self, project_input: Dict[str, Any]) -> str:
        """构建用户提示词"""
        user_input_json = {
            "theme": project_input.get("course_topic", ""),
            "summary": project_input.get("course_overview", ""),
            "ageGroup": project_input.get("age_group", ""),
            "duration": project_input.get("duration", ""),
            "keyTools": project_input.get("ai_tools", "").split(", ") if project_input.get("ai_tools") else []
        }

        return f"""
# USER INPUT
{json.dumps(user_input_json, ensure_ascii=False, indent=2)}

请基于以上输入，生成符合Schema要求的项目基础定义JSON。确保：
1. 驱动性问题具有开放性和吸引力
2. 公开成果具体可执行且符合年龄段
3. 学习目标平衡硬技能和软技能
4. 封面页信息完整且吸引人

直接返回JSON格式，不要任何额外说明。
"""

    async def generate(self, project_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成项目基础定义

        Args:
            project_input: 项目输入数据

        Returns:
            包含生成结果和元数据的字典
        """
        start_time = time.time()

        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(project_input)

            # 调用OpenAI API
            model = settings.agent1_model or settings.openai_model
            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=2000,
                temperature=0.7,
                timeout=self.timeout
            )

            end_time = time.time()
            response_time = end_time - start_time

            if not response["success"]:
                return {
                    "success": False,
                    "error": response.get("error", "Unknown error"),
                    "response_time": response_time,
                    "agent": "project_foundation"
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

                foundation_data = json.loads(content)

                return {
                    "success": True,
                    "data": foundation_data,
                    "response_time": response_time,
                    "token_usage": response["token_usage"],
                    "agent": "project_foundation"
                }

            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": response["content"],
                    "response_time": response_time,
                    "agent": "project_foundation"
                }

        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time": end_time - start_time,
                "agent": "project_foundation"
            }