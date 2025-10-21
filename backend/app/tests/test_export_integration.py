"""
测试导出功能的集成测试
测试完整的HTTP端点、文件名编码、内容验证
"""
import pytest
from fastapi.testclient import TestClient
from urllib.parse import unquote
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.course_project import CourseProject


class TestExportIntegration:
    """导出功能的集成测试"""

    @pytest.fixture
    def client(self):
        """提供测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """提供数据库会话"""
        db = next(get_db())
        yield db
        db.close()

    @pytest.fixture
    def sample_course_with_markdown(self, db_session):
        """创建包含 Markdown 数据的测试课程"""
        course = CourseProject(
            title="0基础AI编程课程",
            subject="计算机科学",
            grade_level="高中",
            duration_weeks=12,
            description="一门面向零基础学生的AI编程课程",
            stage_one_data="""# 阶段一：确定预期学习结果

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
""",
            stage_two_data="""# 阶段二：确定可接受的证据

## 驱动性问题

**如何利用AI技术为社区创造价值？**

### 表现性任务

#### 任务 1: 社区问题调研

**任务描述**: 调研社区存在的实际问题并提出AI解决方案
""",
            stage_three_data="""# 阶段三：规划学习体验

## PBL四阶段流程

### 阶段 1: 项目启动

**时长**: 2周

#### 活动 1.1: 项目介绍

**时间**: 第1周
**活动描述**: 介绍项目背景和目标
**WHERETO原则**: W, H
""",
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        yield course

        # 清理
        db_session.delete(course)
        db_session.commit()

    def test_export_markdown_success(self, client, sample_course_with_markdown):
        """测试成功导出 Markdown"""
        course_id = sample_course_with_markdown.id

        response = client.get(f"/api/v1/courses/{course_id}/export/markdown")

        # 验证响应状态
        assert response.status_code == 200

        # 验证响应头
        assert "text/markdown" in response.headers["content-type"]
        assert "charset=utf-8" in response.headers["content-type"]

        # 验证 Content-Disposition 头（RFC 2231 格式）
        content_disposition = response.headers["content-disposition"]
        assert "attachment" in content_disposition
        assert "filename*=UTF-8''" in content_disposition

        # 提取文件名并解码
        filename_part = content_disposition.split("filename*=UTF-8''")[1]
        decoded_filename = unquote(filename_part)
        assert "0基础AI编程课程" in decoded_filename
        assert "完整版.md" in decoded_filename

        # 验证 Markdown 内容
        markdown_content = response.text

        # 验证课程头部
        assert "# 0基础AI编程课程" in markdown_content
        assert "**学科**: 计算机科学" in markdown_content
        assert "**年级**: 高中" in markdown_content
        assert "**课程时长**: 12周" in markdown_content

        # 验证三个阶段都存在
        assert "阶段一：确定预期学习结果" in markdown_content
        assert "阶段二：确定可接受的证据" in markdown_content
        assert "阶段三：规划学习体验" in markdown_content

        # 验证具体内容
        assert "学生能够应用AI技术解决实际问题" in markdown_content
        assert "如何利用AI技术为社区创造价值？" in markdown_content
        assert "项目介绍" in markdown_content

        # 验证分隔符
        assert "---" in markdown_content

        # 验证底部信息
        assert "本课程方案由 UbD-PBL 课程架构师生成" in markdown_content
        assert "生成时间:" in markdown_content

    def test_export_markdown_course_not_found(self, client):
        """测试导出不存在的课程"""
        response = client.get("/api/v1/courses/99999/export/markdown")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_export_markdown_empty_stages(self, client, db_session):
        """测试导出空阶段数据的课程"""
        course = CourseProject(
            title="空课程",
            stage_one_data=None,
            stage_two_data=None,
            stage_three_data=None,
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        try:
            response = client.get(f"/api/v1/courses/{course.id}/export/markdown")

            # 应该返回 400 错误（至少需要 stage_one_data）
            assert response.status_code == 400
            assert "required" in response.json()["detail"].lower()

        finally:
            db_session.delete(course)
            db_session.commit()

    def test_export_markdown_only_stage_one(self, client, db_session):
        """测试只有 Stage One 数据的课程"""
        course = CourseProject(
            title="部分课程",
            stage_one_data="""# 阶段一：确定预期学习结果

## G: 迁移目标

1. 学生能够独立学习
""",
            stage_two_data=None,
            stage_three_data=None,
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        try:
            response = client.get(f"/api/v1/courses/{course.id}/export/markdown")

            assert response.status_code == 200

            # 验证文件名
            content_disposition = response.headers["content-disposition"]
            filename_part = content_disposition.split("filename*=UTF-8''")[1]
            decoded_filename = unquote(filename_part)
            assert "阶段一" in decoded_filename

            # 验证内容
            markdown_content = response.text
            assert "阶段一：确定预期学习结果" in markdown_content
            assert "阶段二" not in markdown_content
            assert "阶段三" not in markdown_content

        finally:
            db_session.delete(course)
            db_session.commit()

    def test_export_markdown_with_special_characters(self, client, db_session):
        """测试包含特殊字符的课程名称"""
        course = CourseProject(
            title="AI编程 - 从零到一 (2024版)",
            stage_one_data="# 测试内容",
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        try:
            response = client.get(f"/api/v1/courses/{course.id}/export/markdown")

            assert response.status_code == 200

            # 验证文件名包含特殊字符
            content_disposition = response.headers["content-disposition"]
            filename_part = content_disposition.split("filename*=UTF-8''")[1]
            decoded_filename = unquote(filename_part)
            assert "AI编程 - 从零到一 (2024版)" in decoded_filename

        finally:
            db_session.delete(course)
            db_session.commit()

    def test_export_markdown_utf8_encoding(self, client, sample_course_with_markdown):
        """测试 UTF-8 编码正确性"""
        course_id = sample_course_with_markdown.id

        response = client.get(f"/api/v1/courses/{course_id}/export/markdown")

        assert response.status_code == 200

        # 验证响应头声明了 UTF-8 编码
        assert "charset=utf-8" in response.headers["content-type"]

        # 验证内容可以正确编码/解码
        content_bytes = response.content
        content_text = content_bytes.decode("utf-8")

        # 验证中文字符正确
        assert "阶段一" in content_text
        assert "阶段二" in content_text
        assert "阶段三" in content_text
        assert "学生能够" in content_text

        # 验证可以重新编码
        re_encoded = content_text.encode("utf-8")
        assert isinstance(re_encoded, bytes)


class TestExportPerformance:
    """导出功能的性能测试"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        db = next(get_db())
        yield db
        db.close()

    def test_export_large_markdown_content(self, client, db_session):
        """测试导出大型 Markdown 内容"""
        # 创建较大的 Markdown 内容（模拟真实场景）
        large_stage_one = "# 阶段一\n\n" + "## 内容\n\n" * 100
        large_stage_two = "# 阶段二\n\n" + "### 任务\n\n" * 100
        large_stage_three = "# 阶段三\n\n" + "#### 活动\n\n" * 100

        course = CourseProject(
            title="大型课程",
            stage_one_data=large_stage_one,
            stage_two_data=large_stage_two,
            stage_three_data=large_stage_three,
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        try:
            response = client.get(f"/api/v1/courses/{course.id}/export/markdown")

            assert response.status_code == 200

            # 验证内容完整性（不应该被截断）
            content_length = len(response.content)
            assert content_length > 1000  # 至少有合理的长度

        finally:
            db_session.delete(course)
            db_session.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
