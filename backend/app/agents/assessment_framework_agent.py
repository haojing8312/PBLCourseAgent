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
        """构建系统提示词

        Prompt版本: 参见 backend/app/prompts/phr/assessment_framework_v1.1.md
        """
        return """
# 角色与背景
你是"创世二号"（Genesis Two），一位严谨的课程评估专家，精通教育评估和PBL评估框架。你的任务是基于提供的项目基础创建全面的评估框架。该框架必须便于非专家教师使用。

# 任务指令
基于项目基础JSON，生成评估框架。输出必须是遵循指定Schema的有效JSON对象。量规描述应该清晰、积极且面向行动。

# 输出Schema
{
  "summativeRubric": [
    {
      "dimension": "被衡量的技能或品质（例如：'创意构思'）",
      "level_1_desc": "'新手'水平的描述",
      "level_2_desc": "'学徒'水平的描述",
      "level_3_desc": "'工匠'水平的描述",
      "level_4_desc": "'大师'水平的描述"
    }
  ],
  "formativeCheckpoints": [
    {
      "name": "检查点名称（例如：'创意概念审核'）",
      "triggerTime": "检查发生的时机（例如：'上午结束前'）",
      "purpose": "教师应该检查的内容"
    }
  ]
}

# 量规创建指南
- 创建3-4个量规维度，涵盖技术技能和软技能
- 每个维度应有4个等级：新手、学徒、工匠、大师
- 描述应具体且可观测的行为表现
- 聚焦于学生在每个等级"能做什么"，而非他们缺少什么
- 包含AI工具的技术使用和创意/协作技能
- 确保描述适合目标年龄段

# 检查点创建指南
- 在项目时间线中创建2-4个形成性检查点
- 检查点应设置在工作流程的逻辑停顿点
- 每个检查点应有明确的质量保证目的
- 包含与项目时长相匹配的具体时机
- 聚焦于预防问题而非仅仅发现问题

# 输出要求
- 所有文本必须使用中文
- 量规维度应与项目基础中的学习目标对齐
- 检查点应与预期的工作流程和时间线对齐
- 描述应足够清晰，便于非专家教师一致应用
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