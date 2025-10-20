"""
Project Foundation Agent 测试
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from app.agents.project_foundation_agent import ProjectFoundationAgent


@pytest.fixture
def agent():
    """创建Agent实例"""
    return ProjectFoundationAgent()


@pytest.fixture
def sample_input():
    """测试输入数据"""
    return {
        "course_topic": "AI乐队制作人",
        "course_overview": "学生将扮演一个乐队制作人的角色，使用AI工具为一首预设的歌词创作旋律、编曲，并制作一个简单的歌词MV。",
        "age_group": "13-15岁",
        "duration": "2天",
        "ai_tools": "Suno (AI音乐), Runway (AI视频), Canva (平面设计)"
    }


@pytest.fixture
def mock_openai_response():
    """模拟OpenAI响应"""
    return {
        "success": True,
        "content": json.dumps({
            "drivingQuestion": "作为一名新生代的音乐制作人，我们如何仅凭一段文字和强大的AI工具，就能创作出一首能触动人心的歌曲，并为其打造一场完整的、专业的视听发布体验？",
            "publicProduct": {
                "description": "一首完整的原创歌曲及其专业MV，将在课程结束时举办一场'AI音乐发布会'向家长和同学展示。",
                "components": [
                    "一首完整的歌曲 (MP3)：时长1-2分钟",
                    "一个歌词MV (MP4)：AI生成的动态视觉画面组成的音乐视频",
                    "一张数字专辑封面：体现歌曲情绪和风格的专辑封面"
                ]
            },
            "learningObjectives": {
                "hardSkills": [
                    "掌握Suno AI音乐生成工具的基本操作和提示词技巧",
                    "学会使用Runway AI创建动态视觉内容和视频剪辑",
                    "熟练运用Canva进行专辑封面和视觉设计",
                    "了解音乐制作的基本流程：从歌词到旋律到视觉呈现"
                ],
                "softSkills": [
                    "创意表达能力：将抽象的情感和想法转化为具体的音乐和视觉作品",
                    "项目管理能力：在有限时间内协调音乐、视觉、设计多个环节",
                    "审美判断力：对音乐风格、视觉风格的选择和评估能力"
                ]
            },
            "coverPage": {
                "courseTitle": "AI乐队制作人：当文字遇上代码，用AI为诗歌谱写心灵的MV",
                "tagline": "每个人心中都有一首歌，用AI帮你找到它的声音",
                "ageGroup": "13-15岁",
                "duration": "2天 (约16学时)",
                "aiTools": "Suno (AI音乐), Runway (AI视频), Canva (平面设计)"
            }
        }, ensure_ascii=False),
        "response_time": 15.5,
        "token_usage": {
            "prompt_tokens": 500,
            "completion_tokens": 800,
            "total_tokens": 1300
        }
    }


class TestProjectFoundationAgent:

    def test_init(self, agent):
        """测试Agent初始化"""
        assert agent.agent_name == "Genesis One"
        # timeout从配置读取，可能被环境变量覆盖
        assert agent.timeout > 0

    def test_build_system_prompt(self, agent):
        """测试系统提示词构建 - v1.1中文版本"""
        prompt = agent._build_system_prompt()
        assert "Genesis One" in prompt or "创世一号" in prompt
        assert "项目式学习" in prompt or "PBL" in prompt  # 中文化版本
        assert "drivingQuestion" in prompt
        assert "publicProduct" in prompt
        assert "learningObjectives" in prompt

    def test_build_user_prompt(self, agent, sample_input):
        """测试用户提示词构建"""
        prompt = agent._build_user_prompt(sample_input)
        assert "AI乐队制作人" in prompt
        assert "13-15岁" in prompt
        assert "theme" in prompt
        assert "summary" in prompt

    @pytest.mark.asyncio
    async def test_generate_success(self, agent, sample_input, mock_openai_response):
        """测试成功生成"""
        with patch('app.agents.project_foundation_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = mock_openai_response

            result = await agent.generate(sample_input)

            assert result["success"] is True
            assert "data" in result
            assert "response_time" in result
            assert "token_usage" in result
            assert result["agent"] == "project_foundation"

            # 验证数据结构
            data = result["data"]
            assert "drivingQuestion" in data
            assert "publicProduct" in data
            assert "learningObjectives" in data
            assert "coverPage" in data

    @pytest.mark.asyncio
    async def test_generate_openai_error(self, agent, sample_input):
        """测试OpenAI错误处理"""
        with patch('app.agents.project_foundation_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = {
                "success": False,
                "error": "API rate limit exceeded",
                "response_time": 5.0
            }

            result = await agent.generate(sample_input)

            assert result["success"] is False
            assert "API rate limit exceeded" in result["error"]
            assert result["agent"] == "project_foundation"

    @pytest.mark.asyncio
    async def test_generate_json_parse_error(self, agent, sample_input):
        """测试JSON解析错误"""
        with patch('app.agents.project_foundation_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = {
                "success": True,
                "content": "这不是有效的JSON响应",
                "response_time": 10.0,
                "token_usage": {"total_tokens": 100}
            }

            result = await agent.generate(sample_input)

            assert result["success"] is False
            assert "Failed to parse JSON" in result["error"]
            assert "raw_response" in result