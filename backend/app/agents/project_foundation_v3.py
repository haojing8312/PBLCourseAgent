"""
Agent 1 V3: ProjectFoundationAgent - The Strategist
UbD Stage One: 确定预期学习结果 (G/U/Q/K/S框架)
Markdown版本 - 直接生成Markdown文档
"""
import time
from typing import Dict, Any, AsyncGenerator
from pathlib import Path
import logging

from app.core.openai_client import openai_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProjectFoundationAgentV3:
    """
    项目基础定义Agent V3 - Markdown版
    实现UbD Stage One: Desired Results (G/U/Q/K/S)
    直接生成Markdown格式文档，无需JSON解析
    """

    def __init__(self):
        self.agent_name = "The Strategist"
        self.timeout = settings.agent1_timeout or 30
        self.phr_version = "v3.0-markdown"

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
            / "project_foundation_v3_markdown.md"
        )

        if not phr_path.exists():
            logger.error(f"PHR file not found: {phr_path}")
            raise FileNotFoundError(f"PHR v3-markdown prompt file not found: {phr_path}")

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
            logger.info(f"Loaded PHR v3-markdown prompt ({len(system_prompt)} chars)")
            return system_prompt

        except Exception as e:
            logger.error(f"Error parsing PHR file: {e}")
            raise ValueError(f"Failed to parse PHR file: {e}")

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Prompt版本: backend/app/prompts/phr/project_foundation_v3_markdown.md
        """
        return self._load_phr_prompt()

    def _build_user_prompt(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        total_class_hours: int = None,
        schedule_description: str = "",
        description: str = "",
    ) -> str:
        """
        构建用户提示词 - Markdown版本

        Args:
            title: 课程名称
            subject: 学科领域
            grade_level: 年级水平
            total_class_hours: 总课时数（按45分钟标准课时）
            schedule_description: 上课周期描述
            description: 课程简介
        """
        # 构建课程时长信息
        duration_info = ""
        if total_class_hours:
            duration_info = f"{total_class_hours}课时"
        if schedule_description:
            duration_info += f"（{schedule_description}）" if duration_info else schedule_description

        return f"""# USER INPUT
课程名称: {title}
学科领域: {subject or "未指定"}
年级水平: {grade_level or "未指定"}
课程时长: {duration_info or "未指定"}
课程简介: {description or "无"}

请基于以上课程信息，生成符合UbD框架的"阶段一：确定预期学习结果"的完整Markdown文档。

要求：
1. 严格遵循上述模板结构
2. 确保G/U/Q/K/S的内容质量符合指南要求
3. 内容符合目标年龄段的认知水平
4. 直接输出Markdown内容，不要任何包裹或额外说明

开始生成："""

    async def generate(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        total_class_hours: int = None,
        schedule_description: str = "",
        description: str = "",
    ) -> Dict[str, Any]:
        """
        生成Stage One的Markdown文档 (G/U/Q/K/S)

        Args:
            title: 课程名称
            subject: 学科领域
            grade_level: 年级水平
            total_class_hours: 总课时数（按45分钟标准课时）
            schedule_description: 上课周期描述
            description: 课程简介

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
            logger.info(f"Generating Stage One Markdown for: {title}")

            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                title, subject, grade_level, total_class_hours, schedule_description, description
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
                f"Stage One Markdown generated successfully in {generation_time:.2f}s"
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
                "model": settings.agent1_model or settings.openai_model,
            }

    async def generate_stream(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        total_class_hours: int = None,
        schedule_description: str = "",
        description: str = "",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式生成Stage One的Markdown文档 (G/U/Q/K/S)

        Args:
            title: 课程名称
            subject: 学科领域
            grade_level: 年级水平
            total_class_hours: 总课时数（按45分钟标准课时）
            schedule_description: 上课周期描述
            description: 课程简介

        Yields:
            Dict[str, Any]: 流式事件
            {
                "type": "progress",  # "progress" | "complete" | "error"
                "content": str,      # 当前累积的markdown内容
                "chunk": str,        # 本次新增的文本块（仅progress事件）
                "progress": float,   # 0.0-1.0 估算进度
            }
        """
        start_time = time.time()
        accumulated_content = ""
        model = settings.agent1_model or settings.openai_model

        try:
            logger.info(f"Streaming Stage One Markdown for: {title}")

            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                title, subject, grade_level, total_class_hours, schedule_description, description
            )

            # 调用流式AI API
            chunk_count = 0
            start_stream = time.time()
            logger.info("[STREAM] Agent 1 starting OpenAI streaming...")

            async for chunk in openai_client.generate_response_stream(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                max_tokens=3000,
                temperature=0.7,
                timeout=self.timeout,
            ):
                accumulated_content += chunk
                chunk_count += 1
                elapsed = time.time() - start_stream

                # 每10个chunk记录一次日志
                if chunk_count % 10 == 0:
                    logger.info(f"[STREAM] Agent 1 chunk #{chunk_count} @ {elapsed:.2f}s, chars: {len(accumulated_content)}")

                # 🔑 关键：每个chunk都发送进度事件并yield（实时）
                estimated_progress = min(len(accumulated_content) / 2000, 0.99)

                logger.info(f"[STREAM] Agent 1 yielding progress event #{chunk_count}")
                yield {
                    "type": "progress",
                    "content": accumulated_content,
                    "chunk": chunk,
                    "progress": estimated_progress,
                }
                logger.info(f"[STREAM] Agent 1 yielded event #{chunk_count}")

            logger.info(f"[STREAM] Agent 1 finished! Total chunks: {chunk_count}, elapsed: {time.time() - start_stream:.2f}s")

            # 清理markdown格式（移除可能的代码块包裹）
            final_content = accumulated_content.strip()
            if final_content.startswith("```markdown"):
                final_content = final_content[11:].strip()
                if final_content.endswith("```"):
                    final_content = final_content[:-3].strip()
            elif final_content.startswith("```"):
                final_content = final_content[3:].strip()
                if final_content.endswith("```"):
                    final_content = final_content[:-3].strip()

            generation_time = time.time() - start_time

            logger.info(
                f"Stage One Markdown streaming complete in {generation_time:.2f}s"
            )
            logger.info(
                f"Generated markdown length: {len(final_content)} characters"
            )

            # 发送完成事件
            yield {
                "type": "complete",
                "content": final_content,
                "progress": 1.0,
                "generation_time": generation_time,
                "model": model,
            }

        except Exception as e:
            logger.error(f"Agent streaming failed: {e}", exc_info=True)
            generation_time = time.time() - start_time

            yield {
                "type": "error",
                "error": str(e),
                "content": accumulated_content,  # 返回已生成的部分
                "generation_time": generation_time,
                "model": model,
            }

