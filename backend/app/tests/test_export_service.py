"""
测试 Export Service - Markdown 字符串导出功能
"""
import pytest
from app.services.export_service import get_export_service, ExportService


class TestExportServiceMarkdown:
    """测试 Markdown 字符串输入的导出功能"""

    @pytest.fixture
    def export_service(self):
        """提供 export_service 实例"""
        return ExportService()

    @pytest.fixture
    def sample_stage_one_markdown(self):
        """示例 Stage One Markdown"""
        return """# 阶段一：确定预期学习结果

## G: 迁移目标

1. 学生能够应用AI技术解决实际问题

## U: 持续理解

**U1**: AI不仅是工具，更是思维方式

## Q: 基本问题

1. 什么是真正的智能？

## K: 应掌握的知识

- Python基础语法
- 机器学习基本原理

## S: 应形成的技能

- 编程能力
- 问题解决能力
"""

    @pytest.fixture
    def sample_stage_two_markdown(self):
        """示例 Stage Two Markdown"""
        return """# 阶段二：确定可接受的证据

## 驱动性问题

**如何利用AI技术为社区创造价值？**

### 表现性任务

#### 任务 1: 社区问题调研

**任务描述**: 调研社区存在的实际问题
"""

    @pytest.fixture
    def sample_stage_three_markdown(self):
        """示例 Stage Three Markdown"""
        return """# 阶段三：规划学习体验

## PBL四阶段流程

### 阶段 1: 项目启动

**时长**: 2周

#### 活动 1.1: 项目介绍

**时间**: 第1周
**活动描述**: 介绍项目背景和目标
"""

    @pytest.fixture
    def sample_course_info(self):
        """示例课程信息"""
        return {
            "title": "0基础AI编程课程",
            "subject": "计算机科学",
            "grade_level": "高中",
            "duration_weeks": 12,
            "description": "一门面向零基础学生的AI编程课程",
        }

    def test_export_all_three_stages(
        self,
        export_service,
        sample_stage_one_markdown,
        sample_stage_two_markdown,
        sample_stage_three_markdown,
        sample_course_info,
    ):
        """测试导出三个完整阶段"""
        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=sample_stage_two_markdown,
            stage_three_data=sample_stage_three_markdown,
            course_info=sample_course_info,
        )

        # 验证文件名
        assert "0基础AI编程课程" in filename
        assert "完整版" in filename
        assert filename.endswith(".md")

        # 验证 Markdown 内容
        assert "# 0基础AI编程课程" in markdown
        assert "**学科**: 计算机科学" in markdown
        assert "**年级**: 高中" in markdown
        assert "**课程时长**: 12周" in markdown
        assert "**课程简介**: 一门面向零基础学生的AI编程课程" in markdown

        # 验证三个阶段都包含在内
        assert "阶段一：确定预期学习结果" in markdown
        assert "阶段二：确定可接受的证据" in markdown
        assert "阶段三：规划学习体验" in markdown

        # 验证分隔符
        assert "---" in markdown

        # 验证底部信息
        assert "本课程方案由 UbD-PBL 课程架构师生成" in markdown
        assert "生成时间:" in markdown

    def test_export_stage_one_only(
        self, export_service, sample_stage_one_markdown, sample_course_info
    ):
        """测试只导出 Stage One"""
        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=None,
            stage_three_data=None,
            course_info=sample_course_info,
        )

        # 验证文件名
        assert "阶段一" in filename

        # 验证只有 Stage One 内容
        assert "阶段一：确定预期学习结果" in markdown
        assert "阶段二" not in markdown
        assert "阶段三" not in markdown

    def test_export_stage_one_and_two(
        self,
        export_service,
        sample_stage_one_markdown,
        sample_stage_two_markdown,
        sample_course_info,
    ):
        """测试导出 Stage One 和 Stage Two"""
        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=sample_stage_two_markdown,
            stage_three_data=None,
            course_info=sample_course_info,
        )

        # 验证文件名
        assert "阶段一二" in filename

        # 验证包含两个阶段
        assert "阶段一：确定预期学习结果" in markdown
        assert "阶段二：确定可接受的证据" in markdown
        assert "阶段三" not in markdown

    def test_export_with_chinese_filename(
        self, export_service, sample_stage_one_markdown
    ):
        """测试中文文件名生成"""
        course_info = {"title": "零基础AI课程设计"}

        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=None,
            stage_three_data=None,
            course_info=course_info,
        )

        # 验证中文文件名（应该保留中文）
        assert "零基础AI课程设计" in filename
        assert filename.endswith(".md")

    def test_export_without_stage_one_raises_error(self, export_service):
        """测试没有 Stage One 数据时抛出错误"""
        with pytest.raises(ValueError, match="At least stage_one_data is required"):
            export_service.export_for_download(
                stage_one_data=None,
                stage_two_data="some data",
                stage_three_data=None,
                course_info={"title": "测试"},
            )

    def test_export_minimal_course_info(
        self, export_service, sample_stage_one_markdown
    ):
        """测试最小课程信息"""
        # 只有 title
        course_info = {"title": "简单课程"}

        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=None,
            stage_three_data=None,
            course_info=course_info,
        )

        # 验证基本内容
        assert "# 简单课程" in markdown
        # 不应该有学科、年级等信息
        assert "**学科**:" not in markdown
        assert "**年级**:" not in markdown

    def test_export_empty_course_info(
        self, export_service, sample_stage_one_markdown
    ):
        """测试空课程信息（使用默认值）"""
        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=None,
            stage_three_data=None,
            course_info=None,
        )

        # 应该使用默认标题
        assert "未命名课程" in filename
        assert "# 未命名课程" in markdown

    def test_markdown_content_encoding(
        self, export_service, sample_stage_one_markdown, sample_course_info
    ):
        """测试 Markdown 内容包含中文字符"""
        filename, markdown = export_service.export_for_download(
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=None,
            stage_three_data=None,
            course_info=sample_course_info,
        )

        # 验证中文内容正确保留
        assert "学生能够应用AI技术解决实际问题" in markdown
        assert "什么是真正的智能？" in markdown

        # 验证可以编码为 UTF-8
        encoded = markdown.encode("utf-8")
        assert isinstance(encoded, bytes)

        # 验证可以解码回来
        decoded = encoded.decode("utf-8")
        assert decoded == markdown


class TestExportServiceLegacyCompatibility:
    """测试向后兼容性"""

    @pytest.fixture
    def export_service(self):
        return ExportService()

    def test_legacy_methods_still_exist(self, export_service):
        """验证旧的方法仍然存在（用于向后兼容）"""
        # export_to_markdown 方法应该仍然存在
        assert hasattr(export_service, "export_to_markdown")

        # export_stage_one_only 方法应该仍然存在
        assert hasattr(export_service, "export_stage_one_only")


class TestExportServiceSingleton:
    """测试单例模式"""

    def test_get_export_service_returns_singleton(self):
        """验证 get_export_service 返回单例"""
        service1 = get_export_service()
        service2 = get_export_service()

        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
