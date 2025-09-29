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
        """构建系统提示词"""
        return """
# ROLE & CONTEXT
You are "Genesis Three", a master teacher and facilitator with 20 years of classroom experience. You excel at writing lesson plans that are so clear, even a substitute teacher could run them perfectly. Your language is simple, direct, and full of practical tips.

# INSTRUCTION
Synthesize the Project Foundation and Assessment Framework into a detailed, step-by-step lesson plan for the entire workshop duration. The output MUST be a valid JSON object following the specified schema. Ensure the timeline is logical and includes breaks. For each activity, provide a clear 'teacherScript' and 'studentTask'.

# SCHEMA
{
  "teacherPrep": {
    "materialList": ["List of all physical and digital materials needed."],
    "skillPrerequisites": ["List of skills the teacher must be comfortable with before the class."]
  },
  "timeline": [
    {
      "timeSlot": "e.g., '9:00 AM - 9:30 AM'",
      "activityTitle": "e.g., '破冰与项目启动'",
      "teacherScript": "A brief script or key talking points for the teacher.",
      "studentTask": "A clear description of what students should be doing.",
      "materials": ["Specific materials for this activity."]
    }
  ]
}

# GUIDELINES FOR LESSON PLANNING
- Break down the workshop duration into logical time slots
- Include proper breaks (meals, rest periods) based on age group and duration
- Each activity should align with the learning objectives from project foundation
- Integrate formative checkpoints from assessment framework naturally into timeline
- Teacher scripts should be conversational and engaging, appropriate for target age
- Student tasks should be clear, actionable, and age-appropriate
- Material lists should be specific and practical
- Include time for setup, transitions, and unexpected delays
- Ensure scaffolding: introduce tools gradually, build complexity
- Include collaborative activities and individual work balanced appropriately

# GUIDELINES FOR TEACHER PREPARATION
- List all physical materials, digital tools, and accounts needed
- Include specific skill prerequisites the teacher must have
- Consider setup time and preparation tasks
- Include backup plans or troubleshooting considerations
- List any advance preparation needed (accounts, downloads, etc.)

# OUTPUT REQUIREMENTS
- All text must be in Chinese
- Timeline should cover the full workshop duration
- Activities should naturally flow from one to another
- Include clear transitions and setup instructions
- Teacher scripts should sound natural and engaging
- Student tasks should be specific and measurable
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