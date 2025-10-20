"""
Agent 3: 学习蓝图生成 (Learning Blueprint Agent)
"""
import json
import time
from typing import Dict, Any
from app.core.openai_client import openai_client
from app.core.config import settings


class LearningBlueprintAgent:
    """学习蓝图生成Agent"""

    def __init__(self):
        self.agent_name = "Genesis Three"
        self.timeout = settings.agent3_timeout

    def _build_system_prompt(self) -> str:
        """构建系统提示词

        Prompt版本: 参见 backend/app/prompts/phr/learning_blueprint_v1.1.md
        """
        return """
# 角色与背景
你是"创世三号"（Genesis Three），一位拥有20年课堂经验的资深教师和引导者。你擅长编写清晰明了的教案，即使是代课教师也能完美执行。你的语言简洁、直接且充满实用技巧。

# 任务指令
将项目基础和评估框架综合为详细的、逐步推进的完整工作坊教案。输出必须是遵循指定Schema的有效JSON对象。确保时间线合理且包含休息时间。为每个活动提供清晰的"教师脚本"和"学生任务"。

# 输出Schema
{
  "teacherPrep": {
    "materialList": ["所有需要的实体和数字材料清单"],
    "skillPrerequisites": ["教师在上课前必须掌握的技能清单"]
  },
  "timeline": [
    {
      "timeSlot": "例如：'9:00 AM - 9:30 AM'",
      "activityTitle": "例如：'破冰与项目启动'",
      "teacherScript": "教师的简要脚本或关键话术",
      "studentTask": "学生应该做什么的清晰描述",
      "materials": ["本活动所需的具体材料"]
    }
  ]
}

# 教案设计指南
- 将工作坊时长分解为合理的时间段
- 根据年龄段和时长包含适当的休息（用餐、休息时段）
- 每个活动应与项目基础中的学习目标对齐
- 自然地将评估框架中的形成性检查点融入时间线
- 教师脚本应口语化且吸引人，适合目标年龄段
- 学生任务应清晰、可执行且适合年龄段
- 材料清单应具体且实用
- 为设置、过渡和意外延迟留出时间
- 确保循序渐进：逐步引入工具，逐步增加复杂度
- 适当平衡协作活动和个人作业

# 教师准备指南
- 列出所有实体材料、数字工具和所需账号
- 包含教师必须具备的具体技能前提
- 考虑设置时间和准备任务
- 包含备用方案或故障排查建议
- 列出任何需要提前准备的内容（账号、下载等）

# 输出要求
- 所有文本必须使用中文
- 时间线应覆盖完整的工作坊时长
- 活动应自然衔接
- 包含清晰的过渡和设置说明
- 教师脚本应听起来自然且有吸引力
- 学生任务应具体且可衡量
"""

    def _build_user_prompt(self, foundation_data: Dict[str, Any], assessment_data: Dict[str, Any]) -> str:
        """构建用户提示词"""
        return f"""
# PROJECT FOUNDATION
{json.dumps(foundation_data, ensure_ascii=False, indent=2)}

# ASSESSMENT FRAMEWORK
{json.dumps(assessment_data, ensure_ascii=False, indent=2)}

请基于以上项目基础和评估框架，生成符合Schema要求的详细学习蓝图JSON。确保：

1. **教师准备部分**：
   - 材料清单全面且具体，包含数字工具和实体材料
   - 技能前提要求明确，便于教师自我评估和准备

2. **时间线设计**：
   - 根据课程时长({foundation_data.get('coverPage', {}).get('duration', '未指定')})合理分配时间
   - 适合目标年龄段({foundation_data.get('coverPage', {}).get('ageGroup', '未指定')})的注意力规律
   - 包含适当的休息和过渡时间
   - 自然整合评估框架中的形成性检查点

3. **活动设计**：
   - 教师脚本生动有趣，便于课堂实施
   - 学生任务清晰具体，与学习目标对齐
   - 使用的AI工具：{foundation_data.get('coverPage', {}).get('aiTools', '未指定')}
   - 最终成果：{foundation_data.get('publicProduct', {}).get('description', '未指定')}

4. **教学法整合**：
   - 体现项目式学习(PBL)的特点
   - 包含协作学习和个人创作的平衡
   - 循序渐进引入AI工具和技能

直接返回JSON格式，不要任何额外说明。
"""

    async def generate(self, foundation_data: Dict[str, Any], assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成学习蓝图

        Args:
            foundation_data: Agent 1的输出数据
            assessment_data: Agent 2的输出数据

        Returns:
            包含生成结果和元数据的字典
        """
        start_time = time.time()

        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(foundation_data, assessment_data)

            # 调用OpenAI API
            model = settings.agent3_model or settings.openai_model
            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=4000,
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
                    "agent": "learning_blueprint"
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

                blueprint_data = json.loads(content)

                return {
                    "success": True,
                    "data": blueprint_data,
                    "response_time": response_time,
                    "token_usage": response["token_usage"],
                    "agent": "learning_blueprint"
                }

            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": response["content"],
                    "response_time": response_time,
                    "agent": "learning_blueprint"
                }

        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time": end_time - start_time,
                "agent": "learning_blueprint"
            }