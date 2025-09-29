"""
工作流程服务 - 集成三个Agent的串行执行
"""
import time
import asyncio
from typing import Dict, Any
from app.agents.project_foundation_agent import ProjectFoundationAgent
from app.agents.assessment_framework_agent import AssessmentFrameworkAgent
from app.agents.learning_blueprint_agent import LearningBlueprintAgent
from app.models.schemas import ProjectInput, GenerationResult


class WorkflowService:
    """工作流程服务类"""

    def __init__(self):
        self.agent1 = ProjectFoundationAgent()
        self.agent2 = AssessmentFrameworkAgent()
        self.agent3 = LearningBlueprintAgent()

    async def execute_full_workflow(self, project_input: ProjectInput) -> Dict[str, Any]:
        """
        执行完整的三Agent工作流程

        Args:
            project_input: 用户输入的项目数据

        Returns:
            包含完整生成结果和性能数据的字典
        """
        start_time = time.time()
        agent_times = {}
        errors = []

        try:
            # 转换输入格式
            input_dict = {
                "course_topic": project_input.course_topic,
                "course_overview": project_input.course_overview,
                "age_group": project_input.age_group,
                "duration": project_input.duration,
                "ai_tools": project_input.ai_tools
            }

            # 步骤1: 执行Agent 1 - 项目基础定义
            print("🚀 开始执行 Agent 1: 项目基础定义...")
            agent1_result = await self.agent1.generate(input_dict)
            agent_times["agent1"] = agent1_result.get("response_time", 0)

            if not agent1_result["success"]:
                errors.append(f"Agent 1 failed: {agent1_result.get('error', 'Unknown error')}")
                return self._build_error_response("Agent 1 execution failed", errors, agent_times, time.time() - start_time)

            foundation_data = agent1_result["data"]
            print(f"✅ Agent 1 完成，耗时: {agent1_result['response_time']:.2f}秒")

            # 步骤2: 执行Agent 2 - 评估框架设计
            print("🎯 开始执行 Agent 2: 评估框架设计...")
            agent2_result = await self.agent2.generate(foundation_data)
            agent_times["agent2"] = agent2_result.get("response_time", 0)

            if not agent2_result["success"]:
                errors.append(f"Agent 2 failed: {agent2_result.get('error', 'Unknown error')}")
                return self._build_error_response("Agent 2 execution failed", errors, agent_times, time.time() - start_time)

            assessment_data = agent2_result["data"]
            print(f"✅ Agent 2 完成，耗时: {agent2_result['response_time']:.2f}秒")

            # 步骤3: 执行Agent 3 - 学习蓝图生成
            print("📚 开始执行 Agent 3: 学习蓝图生成...")
            agent3_result = await self.agent3.generate(foundation_data, assessment_data)
            agent_times["agent3"] = agent3_result.get("response_time", 0)

            if not agent3_result["success"]:
                errors.append(f"Agent 3 failed: {agent3_result.get('error', 'Unknown error')}")
                return self._build_error_response("Agent 3 execution failed", errors, agent_times, time.time() - start_time)

            blueprint_data = agent3_result["data"]
            print(f"✅ Agent 3 完成，耗时: {agent3_result['response_time']:.2f}秒")

            # 计算总耗时
            total_time = time.time() - start_time
            print(f"🎉 工作流程全部完成！总耗时: {total_time:.2f}秒")

            # 构建完整结果
            result = {
                "success": True,
                "data": {
                    "project_foundation": foundation_data,
                    "assessment_framework": assessment_data,
                    "learning_blueprint": blueprint_data,
                    "metadata": {
                        "total_time": total_time,
                        "agent_times": agent_times,
                        "performance_metrics": self._calculate_performance_metrics(agent_times, total_time),
                        "token_usage": {
                            "agent1": agent1_result.get("token_usage", {}),
                            "agent2": agent2_result.get("token_usage", {}),
                            "agent3": agent3_result.get("token_usage", {}),
                        }
                    }
                },
                "message": "课程方案生成成功"
            }

            return result

        except Exception as e:
            errors.append(f"Workflow execution error: {str(e)}")
            return self._build_error_response("Workflow execution failed", errors, agent_times, time.time() - start_time)

    def _build_error_response(self, message: str, errors: list, agent_times: dict, total_time: float) -> Dict[str, Any]:
        """构建错误响应"""
        return {
            "success": False,
            "message": message,
            "errors": errors,
            "data": None,
            "metadata": {
                "total_time": total_time,
                "agent_times": agent_times,
                "performance_metrics": self._calculate_performance_metrics(agent_times, total_time)
            }
        }

    def _calculate_performance_metrics(self, agent_times: dict, total_time: float) -> Dict[str, Any]:
        """计算性能指标"""
        # PRD中定义的目标时间
        target_times = {
            "agent1": 20,  # Agent 1目标: < 20秒
            "agent2": 25,  # Agent 2目标: < 25秒
            "agent3": 40,  # Agent 3目标: < 40秒
            "total": 90    # 总目标: < 90秒
        }

        metrics = {
            "targets_met": {},
            "performance_summary": {
                "total_target_met": total_time < target_times["total"],
                "total_time": total_time,
                "total_target": target_times["total"]
            }
        }

        # 检查每个Agent是否达到性能目标
        for agent, actual_time in agent_times.items():
            target = target_times.get(agent, 0)
            metrics["targets_met"][agent] = {
                "actual": actual_time,
                "target": target,
                "met": actual_time < target,
                "percentage": (actual_time / target * 100) if target > 0 else 0
            }

        return metrics

    async def health_check(self) -> Dict[str, Any]:
        """健康检查 - 验证所有Agent是否可用"""
        health_status = {
            "workflow_service": "healthy",
            "agents": {},
            "timestamp": time.time()
        }

        try:
            # 简单检查每个Agent的初始化状态
            health_status["agents"]["agent1"] = {
                "name": self.agent1.agent_name,
                "timeout": self.agent1.timeout,
                "status": "ready"
            }
            health_status["agents"]["agent2"] = {
                "name": self.agent2.agent_name,
                "timeout": self.agent2.timeout,
                "status": "ready"
            }
            health_status["agents"]["agent3"] = {
                "name": self.agent3.agent_name,
                "timeout": self.agent3.timeout,
                "status": "ready"
            }

            return {
                "success": True,
                "data": health_status,
                "message": "All agents are healthy and ready"
            }

        except Exception as e:
            return {
                "success": False,
                "data": health_status,
                "message": f"Health check failed: {str(e)}"
            }


# 全局工作流程服务实例
workflow_service = WorkflowService()