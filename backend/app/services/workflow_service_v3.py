"""
Workflow Service V3
整合三个Agent，实现完整的UbD工作流 + SSE流式输出
"""
import asyncio
import json
import time
from typing import Dict, Any, AsyncGenerator
import logging

from app.agents import (
    ProjectFoundationAgentV3,
    AssessmentFrameworkAgentV3,
    LearningBlueprintAgentV3,
)
from app.services.validation_service import get_validation_service
from app.models.stage_data import StageOneData, StageTwoData, StageThreeData

logger = logging.getLogger(__name__)


class WorkflowServiceV3:
    """
    工作流服务V3
    实现三阶段UbD工作流的SSE流式生成
    """

    def __init__(self):
        self.agent1 = ProjectFoundationAgentV3()
        self.agent2 = AssessmentFrameworkAgentV3()
        self.agent3 = LearningBlueprintAgentV3()
        self.validation_service = get_validation_service()

    async def stream_workflow(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        total_class_hours: int = None,
        schedule_description: str = "",
        description: str = "",
        stages_to_generate: list = None,
        stage_one_data: str = None,
        stage_two_data: str = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式生成完整工作流

        Args:
            stage_one_data: 已有的Stage One Markdown数据（用于重新生成时提供）
            stage_two_data: 已有的Stage Two Markdown数据（用于重新生成时提供）

        Yields:
            SSE格式的事件字符串
        """
        if stages_to_generate is None:
            stages_to_generate = [1, 2, 3]

        start_time = time.time()

        try:
            # 发送开始事件
            yield self._format_sse({
                "event": "start",
                "data": {
                    "message": f"开始生成《{title}》的UbD-PBL课程方案",
                    "stages": stages_to_generate,
                },
            })

            # 使用提供的数据（用于跳过已有阶段）
            # stage_one_data 和 stage_two_data 已经作为参数传入（都是Markdown格式）
            stage_three_data = None

            course_info = {
                "title": title,
                "subject": subject,
                "grade_level": grade_level,
                "total_class_hours": total_class_hours,
                "schedule_description": schedule_description,
                "description": description,
            }

            # ===== Stage 1: 确定预期学习结果 (Markdown版 + 流式) =====
            if 1 in stages_to_generate and not stage_one_data:
                yield self._format_sse({
                    "event": "progress",
                    "data": {
                        "stage": 1,
                        "progress": 0,
                        "message": "阶段1：分析课程目标，构建G/U/Q/K/S框架（Markdown格式）...",
                    },
                })

                # 使用流式生成
                async for event in self.agent1.generate_stream(
                    title=title,
                    subject=subject,
                    grade_level=grade_level,
                    total_class_hours=total_class_hours,
                    schedule_description=schedule_description,
                    description=description,
                ):
                    if event["type"] == "progress":
                        # 转发进度事件（包含当前markdown内容）
                        yield self._format_sse({
                            "event": "progress",
                            "data": {
                                "stage": 1,
                                "progress": event["progress"],
                                "message": f"生成中... ({int(event['progress'] * 100)}%)",
                                "markdown_preview": event["content"],  # 实时预览
                            },
                        })
                    elif event["type"] == "complete":
                        # 完成事件
                        stage_one_data = event["content"]
                        yield self._format_sse({
                            "event": "stage_complete",
                            "data": {
                                "stage": 1,
                                "markdown": stage_one_data,
                                "generation_time": event["generation_time"],
                            },
                        })
                        logger.info(
                            f"Stage 1 Markdown complete: {len(stage_one_data)} characters"
                        )
                    elif event["type"] == "error":
                        # 错误事件
                        yield self._format_sse({
                            "event": "error",
                            "data": {
                                "stage": 1,
                                "message": f"阶段1生成失败: {event.get('error')}",
                            },
                        })
                        return

            # ===== Stage 2: 确定可接受的证据 (流式) =====
            if 2 in stages_to_generate and stage_one_data and not stage_two_data:
                yield self._format_sse({
                    "event": "progress",
                    "data": {
                        "stage": 2,
                        "progress": 0,
                        "message": "阶段2：设计驱动性问题和表现性任务...",
                    },
                })

                # 使用流式生成
                async for event in self.agent2.generate_stream(
                    stage_one_data=stage_one_data, course_info=course_info
                ):
                    if event["type"] == "progress":
                        yield self._format_sse({
                            "event": "progress",
                            "data": {
                                "stage": 2,
                                "progress": event["progress"],
                                "message": f"生成中... ({int(event['progress'] * 100)}%)",
                                "markdown_preview": event["content"],
                            },
                        })
                    elif event["type"] == "complete":
                        stage_two_data = event["content"]
                        yield self._format_sse({
                            "event": "stage_complete",
                            "data": {
                                "stage": 2,
                                "markdown": stage_two_data,
                                "generation_time": event["generation_time"],
                            },
                        })
                        logger.info(
                            f"Stage 2 complete: Markdown generated ({len(stage_two_data)} chars)"
                        )
                    elif event["type"] == "error":
                        yield self._format_sse({
                            "event": "error",
                            "data": {
                                "stage": 2,
                                "message": f"阶段2生成失败: {event.get('error')}",
                            },
                        })
                        return

            # ===== Stage 3: 规划学习体验 (流式) =====
            # 注意：Stage 3 现在接收 Stage 2 的 Markdown 数据
            if 3 in stages_to_generate and stage_one_data and stage_two_data:
                yield self._format_sse({
                    "event": "progress",
                    "data": {
                        "stage": 3,
                        "progress": 0,
                        "message": "阶段3：规划PBL四阶段学习蓝图...",
                    },
                })

                # 使用流式生成
                async for event in self.agent3.generate_stream(
                    stage_one_data=stage_one_data,
                    stage_two_data=stage_two_data,
                    course_info=course_info,
                ):
                    if event["type"] == "progress":
                        yield self._format_sse({
                            "event": "progress",
                            "data": {
                                "stage": 3,
                                "progress": event["progress"],
                                "message": f"生成中... ({int(event['progress'] * 100)}%)",
                                "markdown_preview": event["content"],
                            },
                        })
                    elif event["type"] == "complete":
                        stage_three_data = event["content"]
                        yield self._format_sse({
                            "event": "stage_complete",
                            "data": {
                                "stage": 3,
                                "markdown": stage_three_data,
                                "generation_time": event["generation_time"],
                            },
                        })
                        logger.info(
                            f"Stage 3 complete: Markdown generated ({len(stage_three_data)} chars)"
                        )
                    elif event["type"] == "error":
                        yield self._format_sse({
                            "event": "error",
                            "data": {
                                "stage": 3,
                                "message": f"阶段3生成失败: {event.get('error')}",
                            },
                        })
                        return

            # ===== 完成 =====
            total_time = time.time() - start_time
            yield self._format_sse({
                "event": "complete",
                "data": {
                    "message": "课程方案生成完成！",
                    "total_time": round(total_time, 2),
                    "summary": {
                        "stage_one": {
                            "markdown_length": len(stage_one_data) if isinstance(stage_one_data, str) else 0,
                        },
                        "stage_two": {
                            "markdown_length": len(stage_two_data) if isinstance(stage_two_data, str) else 0,
                        },
                        "stage_three": {
                            "markdown_length": len(stage_three_data) if isinstance(stage_three_data, str) else 0,
                        },
                    },
                },
            })

        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            yield self._format_sse({
                "event": "error",
                "data": {"message": str(e), "stage": None},
            })

    def _format_sse(self, event_data: Dict[str, Any]) -> str:
        """
        格式化SSE事件

        Args:
            event_data: 事件数据字典

        Returns:
            SSE格式字符串: "data: {...}\n\n"
        """
        return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

    async def generate_workflow(
        self,
        title: str,
        subject: str = "",
        grade_level: str = "",
        total_class_hours: int = None,
        schedule_description: str = "",
        description: str = "",
    ) -> Dict[str, Any]:
        """
        非流式的完整工作流生成（用于测试）

        Returns:
            {
                "success": bool,
                "stage_one": StageOneData,
                "stage_two": StageTwoData,
                "stage_three": StageThreeData,
                "total_time": float,
                "error": str (if failed)
            }
        """
        start_time = time.time()

        try:
            course_info = {
                "title": title,
                "subject": subject,
                "grade_level": grade_level,
                "total_class_hours": total_class_hours,
                "schedule_description": schedule_description,
                "description": description,
            }

            # Stage 1
            result1 = await self.agent1.generate(
                title, subject, grade_level, total_class_hours, schedule_description, description
            )
            if not result1["success"]:
                return {"success": False, "error": f"Stage 1 failed: {result1['error']}"}

            stage_one_data = result1["data"]

            # Stage 2
            result2 = await self.agent2.generate(stage_one_data, course_info)
            if not result2["success"]:
                return {"success": False, "error": f"Stage 2 failed: {result2['error']}"}

            stage_two_data = result2["data"]

            # Stage 3
            result3 = await self.agent3.generate(
                stage_one_data, stage_two_data, course_info
            )
            if not result3["success"]:
                return {"success": False, "error": f"Stage 3 failed: {result3['error']}"}

            stage_three_data = result3["data"]

            total_time = time.time() - start_time

            return {
                "success": True,
                "stage_one": stage_one_data,
                "stage_two": stage_two_data,
                "stage_three": stage_three_data,
                "total_time": total_time,
            }

        except Exception as e:
            logger.error(f"Workflow generation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


# 全局单例
_workflow_service_v3 = None


def get_workflow_service_v3() -> WorkflowServiceV3:
    """获取工作流服务单例"""
    global _workflow_service_v3
    if _workflow_service_v3 is None:
        _workflow_service_v3 = WorkflowServiceV3()
    return _workflow_service_v3
