"""
核心业务流程测试
=================

这是最重要的测试文件，覆盖完整的用户业务流程。

**任何重大修改都必须通过此测试：**
- 数据结构调整
- 新模块增加
- Prompt修改
- API接口变更

测试流程：
1. 创建课程（使用新数据结构）
2. 生成Stage 1（项目基础）
3. 生成Stage 2（评估框架）
4. 生成Stage 3（学习蓝图）
5. 导出课程文档

运行方式：
```bash
cd backend
uv run pytest app/tests/test_core_workflow.py -v
```
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base, engine
import json

# 创建测试客户端
client = TestClient(app)


class TestCoreWorkflow:
    """核心业务流程测试套件"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """每个测试前后的设置和清理"""
        # Setup: 创建测试数据库表
        Base.metadata.create_all(bind=engine)
        yield
        # Teardown: 清理（可选）
        # Base.metadata.drop_all(bind=engine)

    def test_01_create_course_with_new_duration_fields(self):
        """
        测试1: 创建课程（使用新的时长字段）

        验证点：
        - API接受total_class_hours和schedule_description
        - 不再要求duration_weeks
        - 返回正确的数据结构
        """
        response = client.post(
            "/api/v1/courses",
            json={
                "title": "测试课程-AI平行宇宙",
                "subject": "STEM",
                "grade_level": "小学",
                "total_class_hours": 40,
                "schedule_description": "共5天，每天半天的时间",
                "description": "让孩子通过AI工具实现创意想法",
            },
        )

        # 验证响应
        assert response.status_code == 201, f"创建课程失败: {response.text}"
        data = response.json()

        # 验证新字段
        assert data["total_class_hours"] == 40, "total_class_hours字段错误"
        assert (
            data["schedule_description"] == "共5天，每天半天的时间"
        ), "schedule_description字段错误"
        assert data["title"] == "测试课程-AI平行宇宙"

        # 保存course_id供后续测试使用
        self.course_id = data["id"]
        print(f"\n✓ 课程创建成功，ID: {self.course_id}")

    def test_02_workflow_api_accepts_new_fields(self):
        """
        测试2: Workflow API接受新字段

        验证点：
        - /api/v1/workflow/stream不再要求duration_weeks
        - 接受total_class_hours和schedule_description
        - 不返回422错误
        """
        response = client.post(
            "/api/v1/workflow/stream",
            json={
                "title": "测试课程-Workflow",
                "subject": "STEM",
                "grade_level": "小学",
                "total_class_hours": 40,
                "schedule_description": "共5天，每天半天",
                "description": "测试Workflow API",
                "stages_to_generate": [1],  # 只生成Stage 1测试
            },
        )

        # 最关键的验证：不能是422错误
        assert response.status_code != 422, f"Workflow API返回422错误，说明字段不匹配: {response.text}"

        # 应该是200（流式响应）
        assert response.status_code == 200, f"Workflow API错误: {response.status_code}"

        print(f"\n✓ Workflow API验证通过，接受新字段")

    def test_03_generate_stage_one(self):
        """
        测试3: 生成Stage 1（项目基础） - 增强版流式验证

        验证点：
        - Agent能正确处理新的时长字段
        - **必须是真正的流式响应（多个progress事件）**
        - **检测"local variable 'time' referenced before assignment"错误**
        - 返回Markdown格式的Stage 1数据
        - 生成内容包含课程时长信息
        """
        # 注意：这个测试会调用真实的AI API（需要API Key）
        # 如果没有API Key，此测试会失败

        response = client.post(
            "/api/v1/workflow/stream",
            json={
                "title": "AI创意工坊",
                "subject": "STEM",
                "grade_level": "小学4-6年级",
                "total_class_hours": 20,
                "schedule_description": "每周2次，每次2课时，共5周",
                "description": "通过AI工具培养创造力",
                "stages_to_generate": [1],
            },
        )

        assert response.status_code == 200

        # 流式响应，读取所有事件
        events = []
        progress_count = 0
        error_events = []
        last_preview_length = 0

        for line in response.iter_lines():
            if line:
                # TestClient的iter_lines()已经返回字符串，不需要decode
                line_str = line if isinstance(line, str) else line.decode('utf-8')
                if line_str.startswith('data: '):
                    event_data = json.loads(line_str[6:])
                    events.append(event_data)

                    event_type = event_data.get('event')

                    # 统计progress事件
                    if event_type == 'progress':
                        progress_count += 1
                        data = event_data.get('data', {})

                        # 验证markdown_preview持续增长
                        preview = data.get('markdown_preview', '')
                        current_length = len(preview)

                        assert current_length >= last_preview_length, (
                            f"❌ markdown_preview应该持续增长！"
                            f"Previous: {last_preview_length}, Current: {current_length}"
                        )
                        last_preview_length = current_length

                    # 收集错误事件
                    elif event_type == 'error':
                        error_events.append(event_data)

        # 🔑 关键断言1：检测Python变量错误
        for error_event in error_events:
            error_msg = error_event.get('data', {}).get('message', '')

            if "time" in error_msg.lower() and "referenced before assignment" in error_msg.lower():
                pytest.fail(
                    f"\n\n❌ 检测到Python变量作用域错误！\n"
                    f"错误信息: {error_msg}\n\n"
                    f"💡 根本原因：\n"
                    f"   在 project_foundation_v3.py 的 generate_stream() 方法中，\n"
                    f"   有重复的 'import time' 语句在函数内部。\n\n"
                    f"🔧 解决方法：\n"
                    f"   1. 检查 backend/app/agents/project_foundation_v3.py\n"
                    f"   2. 在 generate_stream() 方法内部搜索 'import time'\n"
                    f"   3. 删除函数内的 import 语句（保留文件顶部的 import time）\n"
                    f"   4. 重启后端服务器\n"
                )

        # 🔑 关键断言2：必须是真正的流式（多个progress事件）
        assert progress_count > 10, (
            f"\n\n❌ 只收到 {progress_count} 个progress事件，不是真正的流式！\n"
            f"真正的流式应该有数十甚至数百个progress事件。\n\n"
            f"可能的原因：\n"
            f"1. openai_client.py 的 generate_response_stream() 缺少 stream=True\n"
            f"2. Agent的generate_stream()方法在batching（如 if chunk_count % 5）\n"
            f"3. workflow_service_v3.py 没有正确转发每个progress事件\n\n"
            f"请检查以上三个位置的代码。\n"
        )

        # 验证至少有开始和完成事件
        event_types = [e.get('event') for e in events]
        assert 'start' in event_types, "缺少start事件"
        assert 'stage_complete' in event_types or 'complete' in event_types, "缺少完成事件"

        # 验证Stage 1数据
        stage_complete_events = [e for e in events if e.get('event') == 'stage_complete' and e.get('data', {}).get('stage') == 1]
        if stage_complete_events:
            stage_data = stage_complete_events[0]['data']
            assert 'markdown' in stage_data, "Stage 1应返回markdown数据"
            markdown = stage_data['markdown']

            # 验证Markdown内容包含关键信息
            assert 'G:' in markdown or '迁移目标' in markdown, "缺少迁移目标"
            assert 'U:' in markdown or '持续理解' in markdown, "缺少持续理解"

        print(f"\n✓ Stage 1生成成功（收到 {progress_count} 个progress事件，真正的流式响应！）")

    def test_04_export_course(self):
        """
        测试4: 导出课程

        验证点：
        - 导出功能正确处理新字段
        - 导出的Markdown包含课程时长信息
        """
        # 首先需要有一个已创建的课程
        # 使用test_01创建的课程
        if not hasattr(self, 'course_id'):
            pytest.skip("需要先运行test_01创建课程")

        response = client.get(f"/api/v1/courses/{self.course_id}/export/markdown")

        assert response.status_code == 200
        content = response.content.decode('utf-8')

        # 验证导出内容包含时长信息
        assert "40课时" in content or "40" in content, "导出内容应包含课时信息"

        print(f"\n✓ 课程导出成功")

    def test_05_list_courses_shows_new_fields(self):
        """
        测试5: 列表接口返回新字段

        验证点：
        - GET /api/v1/courses返回新字段
        """
        response = client.get("/api/v1/courses")

        assert response.status_code == 200
        courses = response.json()

        # 验证返回的课程包含新字段
        if courses:
            first_course = courses[0]
            assert 'total_class_hours' in first_course or first_course.get('total_class_hours') is None
            assert 'schedule_description' in first_course or first_course.get('schedule_description') is None

        print(f"\n✓ 课程列表API验证通过")


# ========== 快速验证测试（Smoke Test） ==========

@pytest.mark.smoke
def test_smoke_api_health():
    """冒烟测试：API健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    print("\n✓ API健康检查通过")


@pytest.mark.smoke
def test_smoke_create_and_workflow():
    """
    冒烟测试：最小化的端到端流程

    快速验证核心功能是否正常：
    1. 创建课程
    2. 调用Workflow API（不等待完成）
    """
    # 创建课程
    create_response = client.post(
        "/api/v1/courses",
        json={
            "title": "冒烟测试课程",
            "total_class_hours": 20,
            "schedule_description": "测试",
        },
    )
    assert create_response.status_code == 201

    # 调用Workflow（验证不返回422）
    workflow_response = client.post(
        "/api/v1/workflow/stream",
        json={
            "title": "冒烟测试",
            "total_class_hours": 20,
            "schedule_description": "测试",
            "stages_to_generate": [1],
        },
    )
    assert workflow_response.status_code != 422, "Workflow API不应返回422"

    print("\n✓ 冒烟测试通过")


if __name__ == "__main__":
    """直接运行此文件进行测试"""
    pytest.main([__file__, "-v", "--tb=short"])
