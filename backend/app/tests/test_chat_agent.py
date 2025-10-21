"""
测试 Course Chat Agent - 单元测试

测试聊天Agent的核心功能，包括：
- 系统提示词构建
- Markdown字符串参数处理
- 配置正确性
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.course_chat_agent import CourseChatAgent, get_chat_agent


class TestCourseChatAgentInit:
    """测试Chat Agent初始化"""

    def test_init_with_default_params(self):
        """测试默认参数初始化"""
        agent = CourseChatAgent(api_key="test_key")

        assert agent.model == "deepseek-chat"
        assert agent.temperature == 0.7
        assert agent.client is not None

    def test_init_with_custom_params(self):
        """测试自定义参数初始化"""
        agent = CourseChatAgent(
            api_key="custom_key",
            model="gpt-4",
            base_url="https://custom.api.com",
            temperature=0.5,
        )

        assert agent.model == "gpt-4"
        assert agent.temperature == 0.5


class TestSystemPromptBuilding:
    """测试系统提示词构建"""

    @pytest.fixture
    def chat_agent(self):
        """提供测试用的Chat Agent"""
        return CourseChatAgent(api_key="test_key")

    @pytest.fixture
    def sample_course_info(self):
        """示例课程信息"""
        return {
            "title": "AI编程课程",
            "subject": "计算机科学",
            "grade_level": "高中",
            "duration_weeks": 12,
            "description": "AI编程入门课程",
        }

    @pytest.fixture
    def sample_stage_one_markdown(self):
        """示例 Stage One Markdown"""
        return """# 阶段一：确定预期学习结果

## G: 迁移目标

1. 学生能够独立完成AI项目

## U: 持续理解

**U1**: AI是解决问题的工具
"""

    @pytest.fixture
    def sample_stage_two_markdown(self):
        """示例 Stage Two Markdown"""
        return """# 阶段二：确定可接受的证据

## 驱动性问题

**如何用AI解决社区问题？**
"""

    def test_build_system_prompt_no_context(self, chat_agent):
        """测试无上下文的系统提示词"""
        prompt = chat_agent._build_system_prompt(current_step=1)

        assert "课程设计专家" in prompt
        assert "UbD" in prompt
        assert "PBL" in prompt
        assert "当前阶段：Stage 1" in prompt

    def test_build_system_prompt_with_course_info(self, chat_agent, sample_course_info):
        """测试包含课程信息的系统提示词"""
        prompt = chat_agent._build_system_prompt(
            current_step=1, course_info=sample_course_info
        )

        assert "AI编程课程" in prompt
        assert "计算机科学" in prompt
        assert "高中" in prompt
        assert "12周" in prompt

    def test_build_system_prompt_with_stage_one_markdown(
        self, chat_agent, sample_course_info, sample_stage_one_markdown
    ):
        """测试包含 Stage One Markdown 的系统提示词"""
        prompt = chat_agent._build_system_prompt(
            current_step=1,
            course_info=sample_course_info,
            stage_one_data=sample_stage_one_markdown,
        )

        # 验证 Markdown 内容被直接包含
        assert "阶段一：确定预期学习结果" in prompt
        assert "学生能够独立完成AI项目" in prompt
        assert "AI是解决问题的工具" in prompt
        assert "已完成 Stage 1 数据（预期学习结果 - Markdown格式）" in prompt

    def test_build_system_prompt_with_all_stages(
        self,
        chat_agent,
        sample_course_info,
        sample_stage_one_markdown,
        sample_stage_two_markdown,
    ):
        """测试包含所有阶段 Markdown 的系统提示词"""
        stage_three_markdown = """# 阶段三：规划学习体验

## 项目启动阶段

**时长**: 2周
"""

        prompt = chat_agent._build_system_prompt(
            current_step=3,
            course_info=sample_course_info,
            stage_one_data=sample_stage_one_markdown,
            stage_two_data=sample_stage_two_markdown,
            stage_three_data=stage_three_markdown,
        )

        # 验证三个阶段的内容都被包含
        assert "阶段一：确定预期学习结果" in prompt
        assert "阶段二：确定可接受的证据" in prompt
        assert "阶段三：规划学习体验" in prompt

        # 验证当前阶段是 Stage 3
        assert "当前阶段：Stage 3" in prompt

    def test_build_system_prompt_no_json_dumps(
        self, chat_agent, sample_stage_one_markdown
    ):
        """测试系统提示词不使用 json.dumps()"""
        prompt = chat_agent._build_system_prompt(
            current_step=1, stage_one_data=sample_stage_one_markdown
        )

        # 验证没有 JSON 序列化痕迹（如 \n 转义）
        assert "\\n" not in prompt
        assert "\\\"" not in prompt

        # 验证是原始 Markdown 格式
        assert "# 阶段一：确定预期学习结果" in prompt


class TestChatStreamMocking:
    """测试流式对话（使用Mock）"""

    @pytest.fixture
    def chat_agent(self):
        return CourseChatAgent(api_key="test_key")

    @pytest.mark.asyncio
    async def test_chat_stream_basic_flow(self, chat_agent):
        """测试基本的流式对话流程"""
        # Mock OpenAI client
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "测试回复"

        async def mock_stream_iterator():
            yield mock_chunk

        mock_stream = MagicMock()
        mock_stream.__aiter__ = lambda self: mock_stream_iterator()

        async def mock_create(*args, **kwargs):
            return mock_stream

        with patch.object(
            chat_agent.client.chat.completions, "create", side_effect=mock_create
        ):
            result_chunks = []
            async for chunk in chat_agent.chat_stream(
                user_message="你好",
                conversation_history=[],
                current_step=1,
            ):
                result_chunks.append(chunk)

            assert len(result_chunks) > 0
            assert "测试回复" in result_chunks

    @pytest.mark.asyncio
    async def test_chat_stream_with_markdown_context(
        self, chat_agent
    ):
        """测试带有 Markdown 上下文的流式对话"""
        stage_one_md = "# Stage One Data"

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "回复"

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [mock_chunk]

        with patch.object(
            chat_agent.client.chat.completions, "create", return_value=mock_stream
        ) as mock_create:
            async for chunk in chat_agent.chat_stream(
                user_message="请解释Stage One",
                conversation_history=[],
                current_step=1,
                stage_one_data=stage_one_md,
            ):
                pass

            # 验证调用参数
            call_args = mock_create.call_args
            messages = call_args.kwargs["messages"]

            # 系统提示词应该包含 Markdown 内容
            system_prompt = messages[0]["content"]
            assert "# Stage One Data" in system_prompt


class TestSingletonPattern:
    """测试单例模式"""

    def test_get_chat_agent_returns_singleton(self):
        """测试 get_chat_agent 返回单例"""
        # 注意：需要先清除全局实例（如果存在）
        from app.agents import course_chat_agent

        course_chat_agent._chat_agent_instance = None

        agent1 = get_chat_agent()
        agent2 = get_chat_agent()

        assert agent1 is agent2

    def test_get_chat_agent_uses_correct_settings(self):
        """测试 get_chat_agent 使用正确的配置"""
        from app.agents import course_chat_agent

        course_chat_agent._chat_agent_instance = None

        # Patch at the import location (inside the function)
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.openai_api_key = "test_api_key"
            mock_settings.openai_model = "test_model"
            mock_settings.openai_base_url = "https://test.api.com"

            agent = get_chat_agent()

            # 验证使用了正确的配置属性名
            assert agent.client.api_key == "test_api_key"
            assert agent.model == "test_model"

        # 清理单例
        course_chat_agent._chat_agent_instance = None


class TestConversationHistory:
    """测试对话历史处理"""

    @pytest.fixture
    def chat_agent(self):
        return CourseChatAgent(api_key="test_key")

    @pytest.mark.asyncio
    async def test_conversation_history_limit(self, chat_agent):
        """测试对话历史数量限制（最多20轮）"""
        # 创建超过20轮的对话历史
        long_history = [
            {"role": "user", "content": f"消息{i}"}
            for i in range(30)
        ]

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "回复"

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [mock_chunk]

        with patch.object(
            chat_agent.client.chat.completions, "create", return_value=mock_stream
        ) as mock_create:
            async for chunk in chat_agent.chat_stream(
                user_message="新消息",
                conversation_history=long_history,
                current_step=1,
            ):
                pass

            # 验证只使用了最近20轮历史
            call_args = mock_create.call_args
            messages = call_args.kwargs["messages"]

            # system (1) + 最近20条历史 + 当前消息 (1) = 22
            assert len(messages) <= 22


class TestNonStreamChat:
    """测试非流式对话"""

    @pytest.fixture
    def chat_agent(self):
        return CourseChatAgent(api_key="test_key")

    @pytest.mark.asyncio
    async def test_chat_non_stream_basic(self, chat_agent):
        """测试非流式对话基本功能"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "完整的AI回复"

        async def mock_create(*args, **kwargs):
            return mock_response

        with patch.object(
            chat_agent.client.chat.completions,
            "create",
            side_effect=mock_create,
        ):
            result = await chat_agent.chat_non_stream(
                user_message="你好",
                conversation_history=[],
                current_step=1,
            )

            assert result == "完整的AI回复"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
