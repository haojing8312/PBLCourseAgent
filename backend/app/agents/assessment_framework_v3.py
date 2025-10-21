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
    评估框架Agent V3 - Markdown版
    实现UbD Stage Two: Determine Acceptable Evidence
    直接生成Markdown格式文档，无需JSON解析
    """

    def __init__(self):
        self.agent_name = "The Assessor"
        self.timeout = settings.agent2_timeout or 35
        self.phr_version = "v3.0-markdown"

    def _load_phr_prompt(self) -> str:
        """
        从PHR文件加载System Prompt
        """
        phr_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "phr"
            / "assessment_framework_v3_markdown.md"
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

        Prompt版本: backend/app/prompts/phr/assessment_framework_v3_markdown.md
        """
        return self._load_phr_prompt()

    def _build_user_prompt(
        self, stage_one_data: str, course_info: Dict[str, Any]
    ) -> str:
        """
        构建用户提示词 - Markdown版本

        Args:
            stage_one_data: Stage One Markdown数据
            course_info: 课程基本信息
        """
        duration_weeks = course_info.get("duration_weeks", 12)
        return f"""# STAGE ONE DATA (来自前一阶段 - Markdown格式)
{stage_one_data}

# COURSE INFO
{json.dumps(course_info, ensure_ascii=False, indent=2)}

请基于以上Stage One数据，生成符合UbD框架的阶段二：确定可接受的证据。

严格要求：
1. 驱动性问题必须包含真实情境、开放性和明确产出物
2. 表现性任务至少3个，覆盖项目不同阶段
3. 每个任务必须有context、role、deliverable
4. 里程碑周次要根据课程总时长 {duration_weeks}周 合理分配
5. 每个任务的rubric必须有2-3个维度，每个维度4个等级
6. 确保所有任务都关联了Stage One的U/S/K元素

直接输出Markdown内容，不要任何包裹或额外说明。"""

    async def generate(
        self, stage_one_data: str, course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成Stage Two的Markdown文档 (驱动性问题 + 表现性任务 + 评估量规)

        Args:
            stage_one_data: Stage One的Markdown数据
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
                f"Generating Stage Two Markdown for: {course_info.get('title', 'Unknown')}"
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
                f"Stage Two Markdown generated successfully in {generation_time:.2f}s"
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
                "model": settings.agent2_model or settings.openai_model,
            }
