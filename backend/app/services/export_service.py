"""
Export Service
将UbD-PBL课程数据导出为Markdown格式教案
"""
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """
    导出服务
    将Stage数据渲染为Markdown教案文档
    """

    def __init__(self):
        # 设置Jinja2环境
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,  # Markdown不需要HTML转义
        )
        logger.info(f"Export service initialized with template dir: {template_dir}")

    def export_to_markdown(
        self,
        stage_one_data: Dict[str, Any],
        stage_two_data: Dict[str, Any],
        stage_three_data: Dict[str, Any],
        course_info: Dict[str, Any],
    ) -> str:
        """
        导出完整的UbD-PBL课程方案为Markdown

        Args:
            stage_one_data: Stage One数据 (G/U/Q/K/S)
            stage_two_data: Stage Two数据 (驱动性问题 + 表现性任务)
            stage_three_data: Stage Three数据 (PBL学习蓝图)
            course_info: 课程基本信息

        Returns:
            str: Markdown格式的完整教案
        """
        try:
            template = self.env.get_template("course_export_v3.md.jinja2")

            # 准备模板数据
            template_data = {
                "stage_one": stage_one_data,
                "stage_two": stage_two_data,
                "stage_three": stage_three_data,
                "course_info": course_info,
                "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # 渲染模板
            markdown_content = template.render(**template_data)

            logger.info(
                f"Exported course '{course_info.get('title', 'Unknown')}' "
                f"to Markdown ({len(markdown_content)} chars)"
            )

            return markdown_content

        except Exception as e:
            logger.error(f"Export to Markdown failed: {e}", exc_info=True)
            raise ValueError(f"Failed to export course: {str(e)}")

    def export_stage_one_only(
        self, stage_one_data: Dict[str, Any], course_info: Dict[str, Any]
    ) -> str:
        """
        仅导出Stage One部分

        Args:
            stage_one_data: Stage One数据
            course_info: 课程基本信息

        Returns:
            str: Markdown格式的Stage One内容
        """
        try:
            markdown_lines = [
                f"# {course_info.get('title', '课程名称')}",
                "",
                "## 阶段一：确定预期学习结果",
                "",
                "### G: 迁移目标",
                "",
            ]

            for i, goal in enumerate(stage_one_data.get("goals", []), 1):
                markdown_lines.append(f"{i}. {goal.get('text', '')}")

            markdown_lines.extend(["", "### U: 持续理解", ""])

            for i, u in enumerate(stage_one_data.get("understandings", []), 1):
                markdown_lines.append(f"**U{i}**: {u.get('text', '')}")
                if u.get("rationale"):
                    markdown_lines.append(f"*理由*: {u.get('rationale')}")
                if u.get("validation_score") is not None:
                    score = u["validation_score"]
                    status = (
                        "✅ 优秀" if score >= 0.85 else "✓ 合格" if score >= 0.7 else "⚠️ 需改进"
                    )
                    markdown_lines.append(f"*验证分数*: {score:.2f} {status}")
                markdown_lines.append("")

            markdown_lines.extend(["### Q: 基本问题", ""])

            for i, q in enumerate(stage_one_data.get("questions", []), 1):
                markdown_lines.append(f"{i}. {q.get('text', '')}")

            markdown_lines.extend(["", "### K: 应掌握知识", ""])

            for k in stage_one_data.get("knowledge", []):
                markdown_lines.append(f"- {k.get('text', '')}")

            markdown_lines.extend(["", "### S: 应形成技能", ""])

            for s in stage_one_data.get("skills", []):
                markdown_lines.append(f"- {s.get('text', '')}")

            return "\n".join(markdown_lines)

        except Exception as e:
            logger.error(f"Export Stage One failed: {e}", exc_info=True)
            raise ValueError(f"Failed to export Stage One: {str(e)}")

    def export_for_download(
        self,
        stage_one_data: Optional[str] = None,
        stage_two_data: Optional[str] = None,
        stage_three_data: Optional[str] = None,
        course_info: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        """
        导出用于下载的Markdown文件（V3版本 - Markdown字符串输入）

        Args:
            stage_one_data: Stage One Markdown字符串（可选）
            stage_two_data: Stage Two Markdown字符串（可选）
            stage_three_data: Stage Three Markdown字符串（可选）
            course_info: 课程基本信息

        Returns:
            tuple[str, str]: (filename, markdown_content)
        """
        if not course_info:
            course_info = {"title": "未命名课程"}

        # 构建 Markdown 内容
        markdown_parts = []

        # 添加课程头部
        title = course_info.get("title", "未命名课程")
        markdown_parts.append(f"# {title}\n\n")

        # 添加课程基本信息
        if course_info.get("subject"):
            markdown_parts.append(f"**学科**: {course_info['subject']}\n\n")
        if course_info.get("grade_level"):
            markdown_parts.append(f"**年级**: {course_info['grade_level']}\n\n")
        if course_info.get("duration_weeks"):
            markdown_parts.append(f"**课程时长**: {course_info['duration_weeks']}周\n\n")
        if course_info.get("description"):
            markdown_parts.append(f"**课程简介**: {course_info['description']}\n\n")

        markdown_parts.append("---\n\n")

        # 拼接各阶段的 Markdown 内容
        if stage_one_data:
            markdown_parts.append(stage_one_data)
            markdown_parts.append("\n\n---\n\n")

        if stage_two_data:
            markdown_parts.append(stage_two_data)
            markdown_parts.append("\n\n---\n\n")

        if stage_three_data:
            markdown_parts.append(stage_three_data)
            markdown_parts.append("\n\n")

        # 添加底部信息
        from datetime import datetime

        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown_parts.append("---\n\n")
        markdown_parts.append(
            "*本课程方案由 UbD-PBL 课程架构师生成*\n\n"
            f"*生成时间: {generation_time}*\n"
        )

        markdown_content = "".join(markdown_parts)

        # 确定文件名
        if stage_one_data and stage_two_data and stage_three_data:
            filename = f"{title}_完整版.md"
        elif stage_one_data and stage_two_data:
            filename = f"{title}_阶段一二.md"
        elif stage_one_data:
            filename = f"{title}_阶段一.md"
        else:
            raise ValueError("At least stage_one_data is required for export")

        logger.info(
            f"Exported course '{title}' to Markdown ({len(markdown_content)} chars)"
        )

        return filename, markdown_content


# 全局单例
_export_service = None


def get_export_service() -> ExportService:
    """获取导出服务单例"""
    global _export_service
    if _export_service is None:
        _export_service = ExportService()
    return _export_service
