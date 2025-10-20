"""
Agent 2 V3: AssessmentFrameworkAgent - The Assessor
UbD Stage Two: 确定可接受的证据 (驱动性问题 + 表现性任务 + 评估量规)
"""
import json
import time
from typing import Dict, Any, List
from pathlib import Path
import logging

from app.core.openai_client import openai_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class AssessmentFrameworkAgentV3:
    """
    评估框架Agent V3
    实现UbD Stage Two: Determine Acceptable Evidence
    """

    def __init__(self):
        self.agent_name = "The Assessor"
        self.timeout = settings.agent2_timeout or 35
        self.phr_version = "v2.0"

    def _load_phr_prompt(self) -> str:
        """
        从PHR文件加载System Prompt
        """
        phr_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "phr"
            / "assessment_framework_v2.md"
        )

        if not phr_path.exists():
            logger.error(f"PHR file not found: {phr_path}")
            raise FileNotFoundError(f"PHR v2 prompt file not found: {phr_path}")

        with open(phr_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取System Prompt部分
        try:
            start_marker = "## System Prompt\n\n```"
            end_marker = "```\n\n---"

            start_idx = content.find(start_marker)
            if start_idx == -1:
                raise ValueError("System Prompt section not found")

            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)

            if end_idx == -1:
                raise ValueError("End of System Prompt not found")

            system_prompt = content[start_idx:end_idx].strip()
            logger.info(f"Loaded PHR v2 prompt ({len(system_prompt)} chars)")
            return system_prompt

        except Exception as e:
            logger.error(f"Error parsing PHR file: {e}")
            raise ValueError(f"Failed to parse PHR file: {e}")

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Prompt版本: backend/app/prompts/phr/assessment_framework_v2.md
        """
        return self._load_phr_prompt()

    def _build_user_prompt(
        self, stage_one_data: Dict[str, Any], course_info: Dict[str, Any]
    ) -> str:
        """
        构建用户提示词

        Args:
            stage_one_data: Stage One数据 (G/U/Q/K/S)
            course_info: 课程基本信息
        """
        user_input_json = {
            "stage_one_data": stage_one_data,
            "course_info": course_info,
        }

        return f"""# STAGE ONE DATA (来自前一阶段)
{json.dumps(stage_one_data, ensure_ascii=False, indent=2)}

# COURSE INFO
{json.dumps(course_info, ensure_ascii=False, indent=2)}

请基于以上Stage One数据，生成符合UbD框架的阶段二：确定可接受的证据。

严格要求：
1. 驱动性问题必须包含真实情境、开放性和明确产出物
2. 每个表现性任务必须有context和student_role
3. linked_ubd_elements必须正确引用Stage One中的U/S/K的索引
4. 每个任务的rubric必须有4个等级且描述清晰
5. 里程碑周次要根据课程总时长合理分配

直接返回JSON格式，不要任何额外说明。"""

    async def generate(
        self, stage_one_data: Dict[str, Any], course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成Stage Two数据 (驱动性问题 + 表现性任务 + 评估量规)

        Args:
            stage_one_data: Stage One的完整数据 (G/U/Q/K/S)
            course_info: 课程基本信息 {title, duration_weeks, ...}

        Returns:
            {
                "success": bool,
                "data": {
                    "driving_question": str,
                    "driving_question_context": str,
                    "performance_tasks": [...],
                    "other_evidence": [...]
                },
                "generation_time": float,
                "model": str,
                "error": str (if failed)
            }
        """
        start_time = time.time()

        try:
            logger.info(
                f"Generating Stage Two for: {course_info.get('title', 'Unknown')}"
            )

            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(stage_one_data, course_info)

            # 调用AI API
            model = settings.agent2_model or settings.openai_model
            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=3500,
                temperature=0.7,
                timeout=self.timeout,
            )

            generation_time = time.time() - start_time

            if not response["success"]:
                logger.error(f"AI generation failed: {response.get('error')}")
                return {
                    "success": False,
                    "error": response.get("error", "AI generation failed"),
                    "generation_time": generation_time,
                    "model": model,
                }

            # 解析JSON响应
            try:
                content = response["content"]
                # 提取JSON
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                stage_two_data = json.loads(content)

                logger.info(
                    f"Stage Two generated successfully in {generation_time:.2f}s"
                )
                logger.info(
                    f"Generated: Driving Question + "
                    f"{len(stage_two_data.get('performance_tasks', []))} Performance Tasks"
                )

                return {
                    "success": True,
                    "data": stage_two_data,
                    "generation_time": generation_time,
                    "model": model,
                }

            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.error(f"Raw content: {response['content'][:500]}...")
                return {
                    "success": False,
                    "error": f"Failed to parse AI response as JSON: {str(e)}",
                    "generation_time": generation_time,
                    "model": model,
                    "raw_content": response["content"],
                }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            generation_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "generation_time": generation_time,
                "model": settings.agent2_model or settings.openai_model,
            }
