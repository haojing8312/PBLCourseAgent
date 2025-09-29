"""
Assessment Framework Agent 测试
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from app.agents.assessment_framework_agent import AssessmentFrameworkAgent


@pytest.fixture
def agent():
    """创建Agent实例"""
    return AssessmentFrameworkAgent()


@pytest.fixture
def sample_foundation_data():
    """测试用的项目基础数据"""
    return {
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
    }


@pytest.fixture
def mock_openai_response():
    """模拟OpenAI响应"""
    return {
        "success": True,
        "content": json.dumps({
            "summativeRubric": [
                {
                    "dimension": "音乐创意与情感表达",
                    "level_1_desc": "能在指导下创作基础的音乐片段，具备初步的情感理解。",
                    "level_2_desc": "能独立创作符合主题的音乐，初步体现个人创意和情感特色。",
                    "level_3_desc": "创作的音乐具有鲜明的风格特征，情感表达准确且有感染力。",
                    "level_4_desc": "音乐创作展现出独特的艺术视角，情感表达深刻且能引发强烈共鸣。"
                },
                {
                    "dimension": "视觉叙事与MV制作",
                    "level_1_desc": "能完成基本的视觉元素制作，理解视觉与音乐的关联性。",
                    "level_2_desc": "能制作符合音乐主题的视觉内容，具备基本的叙事逻辑。",
                    "level_3_desc": "视觉内容与音乐高度吻合，叙事清晰且具有视觉美感。",
                    "level_4_desc": "MV制作展现出专业水准，视觉叙事富有创新性和艺术性。"
                },
                {
                    "dimension": "AI工具整合与流畅度",
                    "level_1_desc": "能在协助下使用AI工具完成基本任务。",
                    "level_2_desc": "能独立操作主要AI工具，理解各工具的基本功能。",
                    "level_3_desc": "熟练使用多个AI工具，能有效整合不同工具的输出。",
                    "level_4_desc": "创造性地运用AI工具，展现出工具使用的高度技巧和创新应用。"
                },
                {
                    "dimension": "项目完成度与专业性",
                    "level_1_desc": "完成项目的基本组件，具备初步的整体性。",
                    "level_2_desc": "完成所有必要组件，项目具有基本的专业呈现效果。",
                    "level_3_desc": "项目完整且精致，展现出良好的专业水准和细节把控。",
                    "level_4_desc": "项目达到专业级别的完成度，细节处理精湛且具有发布价值。"
                }
            ],
            "formativeCheckpoints": [
                {
                    "name": "音乐Demo试听会",
                    "triggerTime": "第一天下午3点",
                    "purpose": "检查学生使用Suno生成的音乐片段质量，组织同伴反馈，确保音乐方向正确。"
                },
                {
                    "name": "视觉素材中期检查",
                    "triggerTime": "第二天上午10点",
                    "purpose": "评估Runway生成的视觉内容是否与音乐匹配，及时调整视觉风格和元素。"
                },
                {
                    "name": "最终作品预览",
                    "triggerTime": "第二天下午4点",
                    "purpose": "完整预览学生的音乐MV作品，确保所有组件协调统一，为最终发布会做准备。"
                }
            ]
        }, ensure_ascii=False),
        "response_time": 18.2,
        "token_usage": {
            "prompt_tokens": 800,
            "completion_tokens": 1200,
            "total_tokens": 2000
        }
    }


class TestAssessmentFrameworkAgent:

    def test_init(self, agent):
        """测试Agent初始化"""
        assert agent.agent_name == "Genesis Two"
        assert agent.timeout == 25  # 来自配置

    def test_build_system_prompt(self, agent):
        """测试系统提示词构建"""
        prompt = agent._build_system_prompt()
        assert "Genesis Two" in prompt
        assert "summativeRubric" in prompt
        assert "formativeCheckpoints" in prompt
        assert "新手" in prompt
        assert "学徒" in prompt
        assert "工匠" in prompt
        assert "大师" in prompt

    def test_build_user_prompt(self, agent, sample_foundation_data):
        """测试用户提示词构建"""
        prompt = agent._build_user_prompt(sample_foundation_data)
        assert "AI乐队制作人" in prompt
        assert "summativeRubric" in prompt
        assert "formativeCheckpoints" in prompt

    @pytest.mark.asyncio
    async def test_generate_success(self, agent, sample_foundation_data, mock_openai_response):
        """测试成功生成"""
        with patch('app.agents.assessment_framework_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = mock_openai_response

            result = await agent.generate(sample_foundation_data)

            assert result["success"] is True
            assert "data" in result
            assert "response_time" in result
            assert "token_usage" in result
            assert result["agent"] == "assessment_framework"

            # 验证数据结构
            data = result["data"]
            assert "summativeRubric" in data
            assert "formativeCheckpoints" in data

            # 验证量规结构
            assert len(data["summativeRubric"]) >= 3
            for rubric in data["summativeRubric"]:
                assert "dimension" in rubric
                assert "level_1_desc" in rubric
                assert "level_2_desc" in rubric
                assert "level_3_desc" in rubric
                assert "level_4_desc" in rubric

            # 验证检查点结构
            assert len(data["formativeCheckpoints"]) >= 2
            for checkpoint in data["formativeCheckpoints"]:
                assert "name" in checkpoint
                assert "triggerTime" in checkpoint
                assert "purpose" in checkpoint

    @pytest.mark.asyncio
    async def test_generate_openai_error(self, agent, sample_foundation_data):
        """测试OpenAI错误处理"""
        with patch('app.agents.assessment_framework_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = {
                "success": False,
                "error": "API timeout",
                "response_time": 25.0
            }

            result = await agent.generate(sample_foundation_data)

            assert result["success"] is False
            assert "API timeout" in result["error"]
            assert result["agent"] == "assessment_framework"

    @pytest.mark.asyncio
    async def test_generate_json_parse_error(self, agent, sample_foundation_data):
        """测试JSON解析错误"""
        with patch('app.agents.assessment_framework_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = {
                "success": True,
                "content": "这不是有效的JSON格式",
                "response_time": 15.0,
                "token_usage": {"total_tokens": 150}
            }

            result = await agent.generate(sample_foundation_data)

            assert result["success"] is False
            assert "Failed to parse JSON" in result["error"]
            assert "raw_response" in result