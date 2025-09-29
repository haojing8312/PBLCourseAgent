"""
Learning Blueprint Agent 测试
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from app.agents.learning_blueprint_agent import LearningBlueprintAgent


@pytest.fixture
def agent():
    """创建Agent实例"""
    return LearningBlueprintAgent()


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
def sample_assessment_data():
    """测试用的评估框架数据"""
    return {
        "summativeRubric": [
            {
                "dimension": "音乐创意与情感表达",
                "level_1_desc": "能在指导下创作基础的音乐片段，具备初步的情感理解。",
                "level_2_desc": "能独立创作符合主题的音乐，初步体现个人创意和情感特色。",
                "level_3_desc": "创作的音乐具有鲜明的风格特征，情感表达准确且有感染力。",
                "level_4_desc": "音乐创作展现出独特的艺术视角，情感表达深刻且能引发强烈共鸣。"
            }
        ],
        "formativeCheckpoints": [
            {
                "name": "音乐Demo试听会",
                "triggerTime": "第一天下午3点",
                "purpose": "检查学生使用Suno生成的音乐片段质量，组织同伴反馈，确保音乐方向正确。"
            },
            {
                "name": "最终作品预览",
                "triggerTime": "第二天下午4点",
                "purpose": "完整预览学生的音乐MV作品，确保所有组件协调统一，为最终发布会做准备。"
            }
        ]
    }


@pytest.fixture
def mock_openai_response():
    """模拟OpenAI响应"""
    return {
        "success": True,
        "content": json.dumps({
            "teacherPrep": {
                "materialList": [
                    "每位学生一台配备耳机的电脑，确保网络连接稳定",
                    "预先注册的Suno AI、Runway AI、Canva账号及使用教程",
                    "音响设备和投影仪用于分享和展示",
                    "便签纸、马克笔用于反馈活动",
                    "预设的歌词素材库（多种情感主题）",
                    "教师示例作品：完整的歌曲+MV+封面"
                ],
                "skillPrerequisites": [
                    "熟练掌握Suno AI音乐生成工具的操作流程和参数设置",
                    "具备Runway AI视频生成和编辑的基本技能",
                    "熟悉Canva平面设计工具的使用方法",
                    "具备引导学生进行创意讨论和反馈的能力",
                    "了解基本的音乐制作流程和术语"
                ]
            },
            "timeline": [
                {
                    "timeSlot": "第一天 9:00 AM - 9:30 AM",
                    "activityTitle": "音乐制作人集结：开启创作之旅",
                    "teacherScript": "欢迎来到AI音乐制作工作坊！今天你们都是制作人，要为文字创作出触动心灵的音乐。我先播放一段我用AI制作的作品...(播放示例) 看，仅仅用几个关键词，AI就帮我创作了这首歌。今天的挑战是：你们能否创作出比我更棒的作品？",
                    "studentTask": "认真聆听教师示例作品，思考自己想要表达的情感主题。从提供的歌词库中选择或自行创作一段歌词作为创作起点。",
                    "materials": ["音响设备", "教师示例作品", "歌词素材库"]
                },
                {
                    "timeSlot": "第一天 9:30 AM - 11:30 AM",
                    "activityTitle": "Suno工作坊：文字变旋律的魔法",
                    "teacherScript": "现在让我们学习第一个魔法咒语——Suno AI！它能将你的文字转化为美妙的旋律。关键在于如何描述你想要的音乐风格。来看我如何操作...(演示Suno界面、参数设置、提示词技巧)",
                    "studentTask": "跟随教师学习Suno AI的操作方法。使用选定的歌词，尝试不同的音乐风格提示词，生成至少3个不同版本的音乐片段。记录下最满意的版本。",
                    "materials": ["电脑", "Suno AI账号", "耳机", "创作记录表"]
                },
                {
                    "timeSlot": "第一天 11:30 AM - 12:00 PM",
                    "activityTitle": "音乐Demo试听会",
                    "teacherScript": "制作人们，是时候分享你们的初期作品了！我们会播放每个人的Demo，大家用便签给出建设性的反馈。记住，我们是在帮助彼此创作出更好的音乐。",
                    "studentTask": "播放自己的音乐Demo给全班听。认真聆听其他同学的作品，用便签写下具体的赞美和建议。收集大家对自己作品的反馈。",
                    "materials": ["音响设备", "便签纸", "马克笔"]
                }
            ]
        }, ensure_ascii=False),
        "response_time": 35.8,
        "token_usage": {
            "prompt_tokens": 1200,
            "completion_tokens": 2800,
            "total_tokens": 4000
        }
    }


class TestLearningBlueprintAgent:

    def test_init(self, agent):
        """测试Agent初始化"""
        assert agent.agent_name == "Genesis Three"
        assert agent.timeout == 40  # 来自配置

    def test_build_system_prompt(self, agent):
        """测试系统提示词构建"""
        prompt = agent._build_system_prompt()
        assert "Genesis Three" in prompt
        assert "teacherPrep" in prompt
        assert "timeline" in prompt
        assert "materialList" in prompt
        assert "teacherScript" in prompt

    def test_build_user_prompt(self, agent, sample_foundation_data, sample_assessment_data):
        """测试用户提示词构建"""
        prompt = agent._build_user_prompt(sample_foundation_data, sample_assessment_data)
        assert "AI乐队制作人" in prompt
        assert "音乐创意与情感表达" in prompt
        assert "教师准备部分" in prompt
        assert "时间线设计" in prompt

    @pytest.mark.asyncio
    async def test_generate_success(self, agent, sample_foundation_data, sample_assessment_data, mock_openai_response):
        """测试成功生成"""
        with patch('app.agents.learning_blueprint_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = mock_openai_response

            result = await agent.generate(sample_foundation_data, sample_assessment_data)

            assert result["success"] is True
            assert "data" in result
            assert "response_time" in result
            assert "token_usage" in result
            assert result["agent"] == "learning_blueprint"

            # 验证数据结构
            data = result["data"]
            assert "teacherPrep" in data
            assert "timeline" in data

            # 验证教师准备结构
            teacher_prep = data["teacherPrep"]
            assert "materialList" in teacher_prep
            assert "skillPrerequisites" in teacher_prep
            assert len(teacher_prep["materialList"]) > 0
            assert len(teacher_prep["skillPrerequisites"]) > 0

            # 验证时间线结构
            timeline = data["timeline"]
            assert len(timeline) > 0
            for activity in timeline:
                assert "timeSlot" in activity
                assert "activityTitle" in activity
                assert "teacherScript" in activity
                assert "studentTask" in activity
                assert "materials" in activity

    @pytest.mark.asyncio
    async def test_generate_openai_error(self, agent, sample_foundation_data, sample_assessment_data):
        """测试OpenAI错误处理"""
        with patch('app.agents.learning_blueprint_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = {
                "success": False,
                "error": "Content policy violation",
                "response_time": 40.0
            }

            result = await agent.generate(sample_foundation_data, sample_assessment_data)

            assert result["success"] is False
            assert "Content policy violation" in result["error"]
            assert result["agent"] == "learning_blueprint"

    @pytest.mark.asyncio
    async def test_generate_json_parse_error(self, agent, sample_foundation_data, sample_assessment_data):
        """测试JSON解析错误"""
        with patch('app.agents.learning_blueprint_agent.openai_client.generate_response',
                   new_callable=AsyncMock) as mock_client:
            mock_client.return_value = {
                "success": True,
                "content": "这是一个无效的JSON响应",
                "response_time": 30.0,
                "token_usage": {"total_tokens": 200}
            }

            result = await agent.generate(sample_foundation_data, sample_assessment_data)

            assert result["success"] is False
            assert "Failed to parse JSON" in result["error"]
            assert "raw_response" in result