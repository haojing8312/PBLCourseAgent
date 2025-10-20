"""
Agent 1 V3: ProjectFoundationAgent - The Strategist
UbD Stage One: 确定预期学习结果 (G/U/Q/K/S框架)
"""
import json
import time
from typing import Dict, Any
from pathlib import Path
import logging

from app.core.openai_client import openai_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProjectFoundationAgentV3:
    """
    项目基础定义Agent V3
    实现UbD Stage One: Desired Results (G/U/Q/K/S)
    """

    def __init__(self):
        self.agent_name = "The Strategist"
        self.timeout = settings.agent1_timeout or 30
        self.phr_version = "v2.0"

    def _load_phr_prompt(self) -> str:
        """
        从PHR文件加载System Prompt

        Returns:
            str: System prompt内容
        """
        phr_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "phr"
            / "project_foundation_v2.md"
        )

        if not phr_path.exists():
            logger.error(f"PHR file not found: {phr_path}")
            raise FileNotFoundError(f"PHR v2 prompt file not found: {phr_path}")

        with open(phr_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取System Prompt部分 (在```和```之间的第一个代码块)
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

        Prompt版本: backend/app/prompts/phr/project_foundation_v2.md
        """
        return self._load_phr_prompt()

    def _build_user_prompt(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        duration_weeks: int = 12,
        description: str = "",
    ) -> str:
        """
        构建用户提示词

        Args:
            title: 课程名称
            subject: 学科领域
            grade_level: 年级水平
            duration_weeks: 课程时长（周）
            description: 课程简介
        """
        user_input_json = {
            "title": title,
            "subject": subject or "未指定",
            "grade_level": grade_level or "未指定",
            "duration_weeks": duration_weeks,
            "description": description or "",
        }

        return f"""# USER INPUT
{json.dumps(user_input_json, ensure_ascii=False, indent=2)}

请基于以上课程信息，生成符合UbD框架的阶段一：确定预期学习结果。

严格遵循G/U/Q/K/S的区分标准，特别注意：
1. U必须是抽象的big ideas，不是具体知识点或技能
2. 每个U包含rationale字段解释为什么这是持续理解
3. K是"知道什么"，S是"会做什么"，两者不可混淆
4. Q应该是开放性问题，引导学生走向U

直接返回JSON格式，不要任何额外说明。"""

    async def generate(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        duration_weeks: int = 12,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        生成Stage One数据 (G/U/Q/K/S)

        Args:
            title: 课程名称
            subject: 学科领域
            grade_level: 年级水平
            duration_weeks: 课程时长（周）
            description: 课程简介

        Returns:
            {
                "success": bool,
                "data": {
                    "goals": [...],
                    "understandings": [...],
                    "questions": [...],
                    "knowledge": [...],
                    "skills": [...]
                },
                "generation_time": float,
                "model": str,
                "error": str (if failed)
            }
        """
        start_time = time.time()

        try:
            logger.info(f"Generating Stage One for: {title}")

            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                title, subject, grade_level, duration_weeks, description
            )

            # 调用AI API
            model = settings.agent1_model or settings.openai_model
            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=3000,
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
                # 尝试提取JSON（如果被markdown包裹）
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                stage_one_data = json.loads(content)

                logger.info(
                    f"Stage One generated successfully in {generation_time:.2f}s"
                )
                logger.info(
                    f"Generated: {len(stage_one_data.get('understandings', []))} U, "
                    f"{len(stage_one_data.get('knowledge', []))} K, "
                    f"{len(stage_one_data.get('skills', []))} S"
                )

                return {
                    "success": True,
                    "data": stage_one_data,
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
                "model": settings.agent1_model or settings.openai_model,
            }
