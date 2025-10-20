"""
Agent 3 V3: LearningBlueprintAgent - The Planner
UbD Stage Three: 规划学习体验 (PBL四阶段 + WHERETO原则)
"""
import json
import time
from typing import Dict, Any
from pathlib import Path
import logging

from app.core.openai_client import openai_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class LearningBlueprintAgentV3:
    """
    学习蓝图Agent V3
    实现UbD Stage Three: Plan Learning Experiences
    """

    def __init__(self):
        self.agent_name = "The Planner"
        self.timeout = settings.agent3_timeout or 40
        self.phr_version = "v2.0"

    def _load_phr_prompt(self) -> str:
        """
        从PHR文件加载System Prompt
        """
        phr_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "phr"
            / "learning_blueprint_v2.md"
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

        Prompt版本: backend/app/prompts/phr/learning_blueprint_v2.md
        """
        return self._load_phr_prompt()

    def _build_user_prompt(
        self,
        stage_one_data: Dict[str, Any],
        stage_two_data: Dict[str, Any],
        course_info: Dict[str, Any],
    ) -> str:
        """
        构建用户提示词

        Args:
            stage_one_data: Stage One数据 (G/U/Q/K/S)
            stage_two_data: Stage Two数据 (驱动性问题 + 表现性任务)
            course_info: 课程基本信息
        """
        # 构建完整的输入数据
        input_data = {
            "stage_one_data": {
                "understandings": stage_one_data.get("understandings", []),
                "skills": stage_one_data.get("skills", []),
                "knowledge": stage_one_data.get("knowledge", []),
            },
            "stage_two_data": {
                "driving_question": stage_two_data.get("driving_question", ""),
                "performance_tasks": stage_two_data.get("performance_tasks", []),
            },
            "course_info": course_info,
        }

        return f"""# STAGE ONE & TWO DATA
{json.dumps(input_data, ensure_ascii=False, indent=2)}

# COURSE INFO
{json.dumps(course_info, ensure_ascii=False, indent=2)}

请基于以上数据，生成符合UbD框架的阶段三：规划PBL学习体验。

严格要求：
1. 必须按4个PBL阶段组织：Launch → Build → Develop → Present
2. 每个活动必须标注1-3个WHERETO原则
3. 至少70%的活动必须标注linked_ubd_elements（引用Stage One的U/S/K索引）
4. Performance Tasks的milestone_week必须有对应的任务提交活动
5. 活动描述要具体可执行，不要模糊的"学习XX"

直接返回JSON格式，不要任何额外说明。"""

    async def generate(
        self,
        stage_one_data: Dict[str, Any],
        stage_two_data: Dict[str, Any],
        course_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成Stage Three数据 (PBL学习蓝图)

        Args:
            stage_one_data: Stage One的完整数据
            stage_two_data: Stage Two的完整数据
            course_info: 课程基本信息 {title, duration_weeks, ...}

        Returns:
            {
                "success": bool,
                "data": {
                    "pbl_phases": [
                        {
                            "phase_type": "launch",
                            "phase_name": "项目启动",
                            "duration_weeks": 2,
                            "order": 0,
                            "activities": [...]
                        }
                    ]
                },
                "generation_time": float,
                "model": str,
                "error": str (if failed)
            }
        """
        start_time = time.time()

        try:
            logger.info(
                f"Generating Stage Three for: {course_info.get('title', 'Unknown')}"
            )

            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                stage_one_data, stage_two_data, course_info
            )

            # 调用AI API
            model = settings.agent3_model or settings.openai_model
            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=4000,
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

                stage_three_data = json.loads(content)

                # 统计活动数量
                total_activities = sum(
                    len(phase.get("activities", []))
                    for phase in stage_three_data.get("pbl_phases", [])
                )

                logger.info(
                    f"Stage Three generated successfully in {generation_time:.2f}s"
                )
                logger.info(
                    f"Generated: {len(stage_three_data.get('pbl_phases', []))} PBL Phases, "
                    f"{total_activities} Activities"
                )

                return {
                    "success": True,
                    "data": stage_three_data,
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
                "model": settings.agent3_model or settings.openai_model,
            }
