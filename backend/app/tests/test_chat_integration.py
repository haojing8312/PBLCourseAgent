"""
测试 Chat API - 集成测试

测试完整的HTTP端点、SSE流式响应、Markdown上下文处理
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock, AsyncMock
import json

from app.main import app
from app.core.database import get_db
from app.models.course_project import CourseProject


class TestChatStreamIntegration:
    """测试流式对话API集成"""

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
            title="AI编程课程",
            subject="计算机科学",
            grade_level="高中",
            duration_weeks=12,
            description="AI编程入门",
            stage_one_data="""# 阶段一：确定预期学习结果

## G: 迁移目标

1. 学生能够应用AI技术解决实际问题

## U: 持续理解

**U1**: AI不仅是工具，更是思维方式
""",
            stage_two_data="""# 阶段二：确定可接受的证据

## 驱动性问题

**如何利用AI技术为社区创造价值？**
""",
            stage_three_data=None,
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        yield course

        # 清理
        db_session.delete(course)
        db_session.commit()

    @pytest.mark.asyncio
    async def test_chat_stream_endpoint_success(
        self, client, sample_course_with_markdown
    ):
        """测试流式对话端点成功响应"""
        course_id = sample_course_with_markdown.id

        # Mock AI响应
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "AI回复内容"

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [mock_chunk]

        with patch(
            "app.agents.course_chat_agent.AsyncOpenAI"
        ) as mock_openai_class:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_stream)
            mock_openai_class.return_value = mock_client

            # 重置单例以使用Mock
            from app.agents import course_chat_agent
            course_chat_agent._chat_agent_instance = None

            request_data = {
                "course_id": course_id,
                "message": "请解释Stage One的目标",
                "current_step": 1,
                "conversation_history": [],
            }

            response = client.post("/api/v1/chat/stream", json=request_data)

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

            # 验证SSE格式
            content = response.text
            assert "data:" in content

            # 重置单例
            course_chat_agent._chat_agent_instance = None

    def test_chat_stream_endpoint_course_not_found(self, client):
        """测试课程不存在时的错误处理"""
        request_data = {
            "course_id": 99999,
            "message": "测试消息",
            "current_step": 1,
            "conversation_history": [],
        }

        response = client.post("/api/v1/chat/stream", json=request_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_chat_stream_endpoint_invalid_step(self, client, sample_course_with_markdown):
        """测试无效的步骤参数"""
        course_id = sample_course_with_markdown.id

        request_data = {
            "course_id": course_id,
            "message": "测试消息",
            "current_step": 5,  # 无效：应该是1-3
            "conversation_history": [],
        }

        response = client.post("/api/v1/chat/stream", json=request_data)

        # 应该返回验证错误
        assert response.status_code == 422

    def test_chat_stream_with_conversation_history(
        self, client, sample_course_with_markdown
    ):
        """测试带有对话历史的请求"""
        course_id = sample_course_with_markdown.id

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "回复"

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [mock_chunk]

        with patch(
            "app.agents.course_chat_agent.AsyncOpenAI"
        ) as mock_openai_class:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_stream)
            mock_openai_class.return_value = mock_client

            from app.agents import course_chat_agent
            course_chat_agent._chat_agent_instance = None

            request_data = {
                "course_id": course_id,
                "message": "继续上一个话题",
                "current_step": 1,
                "conversation_history": [
                    {"role": "user", "content": "什么是UbD?"},
                    {"role": "assistant", "content": "UbD是为理解而设计..."},
                ],
            }

            response = client.post("/api/v1/chat/stream", json=request_data)

            assert response.status_code == 200

            course_chat_agent._chat_agent_instance = None


class TestChatNonStreamIntegration:
    """测试非流式对话API集成"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        db = next(get_db())
        yield db
        db.close()

    @pytest.fixture
    def sample_course(self, db_session):
        """创建测试课程"""
        course = CourseProject(
            title="测试课程",
            stage_one_data="# Stage One Data",
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        yield course

        db_session.delete(course)
        db_session.commit()

    @pytest.mark.asyncio
    async def test_chat_non_stream_endpoint_success(self, client, sample_course):
        """测试非流式对话端点成功响应"""
        course_id = sample_course.id

        # Mock AI响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "完整的AI回复"

        with patch(
            "app.agents.course_chat_agent.AsyncOpenAI"
        ) as mock_openai_class:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai_class.return_value = mock_client

            from app.agents import course_chat_agent
            course_chat_agent._chat_agent_instance = None

            request_data = {
                "course_id": course_id,
                "message": "你好",
                "current_step": 1,
                "conversation_history": [],
            }

            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200

            data = response.json()
            assert "message" in data
            assert data["message"] == "完整的AI回复"
            assert data["course_id"] == course_id

            course_chat_agent._chat_agent_instance = None


class TestChatMarkdownContext:
    """测试 Markdown 上下文传递"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        db = next(get_db())
        yield db
        db.close()

    @pytest.fixture
    def course_with_all_stages(self, db_session):
        """创建包含所有三个阶段的课程"""
        course = CourseProject(
            title="完整课程",
            stage_one_data="""# 阶段一
## G: 迁移目标
1. 学习AI""",
            stage_two_data="""# 阶段二
## 驱动性问题
如何学习？""",
            stage_three_data="""# 阶段三
## 学习蓝图
项目启动""",
        )

        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        yield course

        db_session.delete(course)
        db_session.commit()

    @pytest.mark.asyncio
    async def test_markdown_context_passed_to_agent(
        self, client, course_with_all_stages
    ):
        """测试 Markdown 上下文正确传递给Agent"""
        course_id = course_with_all_stages.id

        captured_messages = []

        async def capture_create_call(*args, **kwargs):
            """捕获传递给OpenAI的消息"""
            captured_messages.append(kwargs.get("messages", []))

            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta.content = "回复"

            mock_stream = AsyncMock()
            mock_stream.__aiter__.return_value = [mock_chunk]
            return mock_stream

        with patch(
            "app.agents.course_chat_agent.AsyncOpenAI"
        ) as mock_openai_class:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=capture_create_call
            )
            mock_openai_class.return_value = mock_client

            from app.agents import course_chat_agent
            course_chat_agent._chat_agent_instance = None

            request_data = {
                "course_id": course_id,
                "message": "请总结所有阶段",
                "current_step": 3,
                "conversation_history": [],
            }

            response = client.post("/api/v1/chat/stream", json=request_data)

            assert response.status_code == 200

            # 验证系统提示词包含了三个阶段的 Markdown 内容
            assert len(captured_messages) > 0
            system_prompt = captured_messages[0][0]["content"]

            assert "阶段一" in system_prompt
            assert "学习AI" in system_prompt
            assert "阶段二" in system_prompt
            assert "如何学习？" in system_prompt
            assert "阶段三" in system_prompt
            assert "项目启动" in system_prompt

            course_chat_agent._chat_agent_instance = None


class TestChatRequestValidation:
    """测试请求参数验证"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_missing_required_fields(self, client):
        """测试缺少必填字段"""
        # 缺少 course_id
        response = client.post(
            "/api/v1/chat/stream",
            json={"message": "测试", "current_step": 1},
        )

        assert response.status_code == 422

    def test_empty_message(self, client):
        """测试空消息"""
        response = client.post(
            "/api/v1/chat/stream",
            json={"course_id": 1, "message": "", "current_step": 1},
        )

        # 应该返回验证错误（min_length=1）
        assert response.status_code == 422

    def test_invalid_conversation_history_format(self, client):
        """测试无效的对话历史格式"""
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "course_id": 1,
                "message": "测试",
                "current_step": 1,
                "conversation_history": "invalid_format",  # 应该是列表
            },
        )

        assert response.status_code == 422


class TestSSEFormat:
    """测试SSE格式正确性"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        db = next(get_db())
        yield db
        db.close()

    @pytest.fixture
    def sample_course(self, db_session):
        course = CourseProject(title="测试", stage_one_data="# Test")
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        yield course

        db_session.delete(course)
        db_session.commit()

    @pytest.mark.asyncio
    async def test_sse_event_format(self, client, sample_course):
        """测试SSE事件格式"""
        course_id = sample_course.id

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "测试内容"

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [mock_chunk]

        with patch(
            "app.agents.course_chat_agent.AsyncOpenAI"
        ) as mock_openai_class:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_stream)
            mock_openai_class.return_value = mock_client

            from app.agents import course_chat_agent
            course_chat_agent._chat_agent_instance = None

            request_data = {
                "course_id": course_id,
                "message": "测试",
                "current_step": 1,
                "conversation_history": [],
            }

            response = client.post("/api/v1/chat/stream", json=request_data)

            assert response.status_code == 200

            # 解析SSE事件
            events = []
            for line in response.text.split("\n\n"):
                if line.startswith("data: "):
                    event_data = json.loads(line[6:])
                    events.append(event_data)

            # 验证事件顺序：start -> chunk -> done
            assert len(events) >= 3
            assert events[0]["type"] == "start"
            assert any(e["type"] == "chunk" for e in events)
            assert events[-1]["type"] == "done"

            course_chat_agent._chat_agent_instance = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
