"""
工作流程服务测试
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.core.workflow_service import WorkflowService
from app.models.schemas import ProjectInput


@pytest.fixture
def workflow_service():
    """创建工作流程服务实例"""
    return WorkflowService()


@pytest.fixture
def sample_project_input():
    """测试输入数据"""
    return ProjectInput(
        course_topic="AI乐队制作人",
        course_overview="学生将扮演一个乐队制作人的角色，使用AI工具为一首预设的歌词创作旋律、编曲，并制作一个简单的歌词MV。",
        age_group="13-15岁",
        duration="2天",
        ai_tools="Suno (AI音乐), Runway (AI视频), Canva (平面设计)"
    )


@pytest.fixture
def mock_agent_responses():
    """模拟Agent响应"""
    return {
        "agent1": {
            "success": True,
            "data": {
                "drivingQuestion": "作为一名新生代的音乐制作人，我们如何创作出触动人心的歌曲？",
                "publicProduct": {"description": "一首完整的原创歌曲及其专业MV"},
                "learningObjectives": {"hardSkills": [], "softSkills": []},
                "coverPage": {"courseTitle": "AI乐队制作人", "duration": "2天"}
            },
            "response_time": 15.0,
            "token_usage": {"total_tokens": 1000}
        },
        "agent2": {
            "success": True,
            "data": {
                "summativeRubric": [{"dimension": "音乐创意", "level_1_desc": "基础"}],
                "formativeCheckpoints": [{"name": "音乐Demo试听会", "triggerTime": "第一天下午"}]
            },
            "response_time": 20.0,
            "token_usage": {"total_tokens": 1500}
        },
        "agent3": {
            "success": True,
            "data": {
                "teacherPrep": {"materialList": ["电脑", "软件"], "skillPrerequisites": ["音乐基础"]},
                "timeline": [{"timeSlot": "9:00-10:00", "activityTitle": "开场"}]
            },
            "response_time": 35.0,
            "token_usage": {"total_tokens": 2000}
        }
    }


class TestWorkflowService:

    def test_init(self, workflow_service):
        """测试工作流程服务初始化"""
        assert workflow_service.agent1 is not None
        assert workflow_service.agent2 is not None
        assert workflow_service.agent3 is not None
        assert workflow_service.agent1.agent_name == "Genesis One"
        assert workflow_service.agent2.agent_name == "Genesis Two"
        assert workflow_service.agent3.agent_name == "Genesis Three"

    def test_calculate_performance_metrics(self, workflow_service):
        """测试性能指标计算"""
        agent_times = {
            "agent1": 15.0,
            "agent2": 20.0,
            "agent3": 35.0
        }
        total_time = 70.0

        metrics = workflow_service._calculate_performance_metrics(agent_times, total_time)

        assert "targets_met" in metrics
        assert "performance_summary" in metrics

        # 检查总体性能
        assert metrics["performance_summary"]["total_target_met"] is True  # 70 < 90
        assert metrics["performance_summary"]["total_time"] == 70.0

        # 检查各Agent性能
        assert metrics["targets_met"]["agent1"]["met"] is True  # 15 < 20
        assert metrics["targets_met"]["agent2"]["met"] is True  # 20 < 25
        assert metrics["targets_met"]["agent3"]["met"] is True  # 35 < 40

    def test_build_error_response(self, workflow_service):
        """测试错误响应构建"""
        errors = ["Agent 1 failed", "Network timeout"]
        agent_times = {"agent1": 25.0}
        total_time = 30.0

        response = workflow_service._build_error_response(
            "Test error", errors, agent_times, total_time
        )

        assert response["success"] is False
        assert response["message"] == "Test error"
        assert response["errors"] == errors
        assert response["data"] is None
        assert response["metadata"]["total_time"] == 30.0

    @pytest.mark.asyncio
    async def test_execute_full_workflow_success(self, workflow_service, sample_project_input, mock_agent_responses):
        """测试成功执行完整工作流程"""
        with patch.object(workflow_service.agent1, 'generate', new_callable=AsyncMock) as mock_agent1, \
             patch.object(workflow_service.agent2, 'generate', new_callable=AsyncMock) as mock_agent2, \
             patch.object(workflow_service.agent3, 'generate', new_callable=AsyncMock) as mock_agent3:

            # 设置mock响应
            mock_agent1.return_value = mock_agent_responses["agent1"]
            mock_agent2.return_value = mock_agent_responses["agent2"]
            mock_agent3.return_value = mock_agent_responses["agent3"]

            result = await workflow_service.execute_full_workflow(sample_project_input)

            # 验证结果
            assert result["success"] is True
            assert "data" in result
            assert result["message"] == "课程方案生成成功"

            # 验证数据结构
            data = result["data"]
            assert "project_foundation" in data
            assert "assessment_framework" in data
            assert "learning_blueprint" in data
            assert "metadata" in data

            # 验证元数据
            metadata = data["metadata"]
            assert "total_time" in metadata
            assert "agent_times" in metadata
            assert "performance_metrics" in metadata
            assert "token_usage" in metadata

            # 验证Agent调用
            mock_agent1.assert_called_once()
            mock_agent2.assert_called_once()
            mock_agent3.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_full_workflow_agent1_failure(self, workflow_service, sample_project_input):
        """测试Agent 1失败的情况"""
        with patch.object(workflow_service.agent1, 'generate', new_callable=AsyncMock) as mock_agent1:
            mock_agent1.return_value = {
                "success": False,
                "error": "API rate limit exceeded",
                "response_time": 5.0
            }

            result = await workflow_service.execute_full_workflow(sample_project_input)

            assert result["success"] is False
            assert "Agent 1 execution failed" in result["message"]
            assert "API rate limit exceeded" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_execute_full_workflow_agent2_failure(self, workflow_service, sample_project_input, mock_agent_responses):
        """测试Agent 2失败的情况"""
        with patch.object(workflow_service.agent1, 'generate', new_callable=AsyncMock) as mock_agent1, \
             patch.object(workflow_service.agent2, 'generate', new_callable=AsyncMock) as mock_agent2:

            mock_agent1.return_value = mock_agent_responses["agent1"]
            mock_agent2.return_value = {
                "success": False,
                "error": "Model overloaded",
                "response_time": 10.0
            }

            result = await workflow_service.execute_full_workflow(sample_project_input)

            assert result["success"] is False
            assert "Agent 2 execution failed" in result["message"]
            assert "Model overloaded" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_health_check(self, workflow_service):
        """测试健康检查"""
        result = await workflow_service.health_check()

        assert result["success"] is True
        assert "All agents are healthy" in result["message"]

        data = result["data"]
        assert "workflow_service" in data
        assert "agents" in data
        assert "timestamp" in data

        # 检查每个Agent的状态
        agents = data["agents"]
        assert "agent1" in agents
        assert "agent2" in agents
        assert "agent3" in agents

        for agent_key, agent_info in agents.items():
            assert "name" in agent_info
            assert "timeout" in agent_info
            assert agent_info["status"] == "ready"