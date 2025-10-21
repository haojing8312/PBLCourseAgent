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
    学习蓝图Agent V3 - Markdown版
    实现UbD Stage Three: Plan Learning Experiences
    直接生成Markdown格式文档，接收Markdown格式的Stage One和Stage Two数据
    """

    def __init__(self):
        self.agent_name = "The Planner"
        self.timeout = settings.agent3_timeout or 40
        self.phr_version = "v3.0-markdown"

    def _load_phr_prompt(self) -> str:
        """
        从PHR文件加载System Prompt
        """
        phr_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "phr"
            / "learning_blueprint_v3_markdown.md"
        )

        if not phr_path.exists():
            logger.error(f"PHR file not found: {phr_path}")
            raise FileNotFoundError(f"PHR v3-markdown prompt file not found: {phr_path}")

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
            logger.info(f"Loaded PHR v3-markdown prompt ({len(system_prompt)} chars)")
            return system_prompt

        except Exception as e:
            logger.error(f"Error parsing PHR file: {e}")
            raise ValueError(f"Failed to parse PHR file: {e}")

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Prompt版本: backend/app/prompts/phr/learning_blueprint_v3_markdown.md
        """
        return self._load_phr_prompt()

    def _build_user_prompt(
        self,
        stage_one_data: str,
        stage_two_data: str,
        course_info: Dict[str, Any],
    ) -> str:
        """
        构建用户提示词 - Markdown版本

        Args:
            stage_one_data: Stage One Markdown数据
            stage_two_data: Stage Two Markdown数据
            course_info: 课程基本信息
        """
        duration_weeks = course_info.get("duration_weeks", 12)
        return f"""# STAGE ONE DATA (Markdown格式)
{stage_one_data}

# STAGE TWO DATA (Markdown格式)
{stage_two_data}

# COURSE INFO
{json.dumps(course_info, ensure_ascii=False, indent=2)}

请基于以上数据，生成符合UbD框架的阶段三：规划PBL学习体验。

严格要求：
1. 必须按4个PBL阶段组织：Launch → Build → Develop → Present
2. 每个阶段包含多个具体活动，活动总数应该在12-20个之间
3. 每个活动必须标注1-3个WHERETO原则
4. 至少70%的活动必须标注linked UbD elements（U/S/K）
5. Performance Tasks的milestone_week必须有对应的任务提交活动
6. 活动描述要具体可执行，不要模糊的"学习XX"
7. 课程总时长为 {duration_weeks}周，四个阶段合理分配

直接输出Markdown内容，不要任何包裹或额外说明。"""

    async def generate(
        self,
        stage_one_data: str,
        stage_two_data: str,
        course_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成Stage Three的Markdown文档 (PBL学习蓝图)

        Args:
            stage_one_data: Stage One的Markdown数据
            stage_two_data: Stage Two的Markdown数据
            course_info: 课程基本信息 {title, duration_weeks, ...}

        Returns:
            {
                "success": bool,
                "markdown": str,  # Markdown文档字符串
                "generation_time": float,
                "model": str,
                "error": str (if failed)
            }
        """
        start_time = time.time()

        try:
            logger.info(
                f"Generating Stage Three Markdown for: {course_info.get('title', 'Unknown')}"
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

            # 直接返回Markdown内容，无需JSON解析
            markdown_content = response["content"].strip()

            # 移除可能的markdown代码块包裹
            if markdown_content.startswith("```markdown"):
                markdown_content = markdown_content[11:].strip()
                if markdown_content.endswith("```"):
                    markdown_content = markdown_content[:-3].strip()
            elif markdown_content.startswith("```"):
                markdown_content = markdown_content[3:].strip()
                if markdown_content.endswith("```"):
                    markdown_content = markdown_content[:-3].strip()

            logger.info(
                f"Stage Three Markdown generated successfully in {generation_time:.2f}s"
            )
            logger.info(
                f"Generated markdown length: {len(markdown_content)} characters"
            )

            return {
                "success": True,
                "markdown": markdown_content,
                "generation_time": generation_time,
                "model": model,
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
