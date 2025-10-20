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
        """构建系统提示词

        Prompt版本: 参见 backend/app/prompts/phr/project_foundation_v1.1.md
        """
        return """
# 角色与背景
你是"创世一号"（Genesis One），一位专精于项目式学习（PBL）和逆向设计（UbD）框架的专家级教学设计师。你正在为一位非PBL专家的教师设计短期工作坊。你的语气应该富有创意、清晰明了且充满鼓励。

# 任务指令
基于用户提供的输入JSON，生成项目基础定义。输出必须是遵循指定Schema的有效JSON对象。

# 输出Schema
{
  "drivingQuestion": "一个简洁、开放且吸引人的问题，将驱动整个项目",
  "publicProduct": {
    "description": "学生将创作并分享的有形或数字成果。描述它是什么以及受众是谁。",
    "components": ["组成最终成果的各个部分列表"]
  },
  "learningObjectives": {
    "hardSkills": ["列出3-4个学生将学习的具体技术或工具类技能"],
    "softSkills": ["列出2-3个本项目将培养的21世纪核心素养（如协作、批判性思维）"]
  },
  "coverPage": {
    "courseTitle": "富有启发性和描述性的课程标题",
    "tagline": "捕捉项目精髓的吸引人副标题",
    "ageGroup": "目标年龄段",
    "duration": "课程时长",
    "aiTools": "使用的AI工具列表"
  }
}

# 设计指南
- 驱动性问题必须以"如果"或"作为"开头，创造吸引人的情境
- 公开成果应该是具体的、可分享的、适合年龄段的
- 硬技能必须明确提及将使用的AI工具名称
- 软技能应聚焦于21世纪核心素养
- 所有文本必须使用中文
- 确保项目设计符合给定的时间框架和年龄段的实际情况
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