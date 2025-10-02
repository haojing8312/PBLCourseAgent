"""
分阶段生成的简化Agent实现
这些Agent专门用于人工参与式工作流,接受自由文本输入,返回Markdown格式输出
"""
from app.core.openai_client import openai_client
from app.core.config import settings
import time


class Stage1Agent:
    """阶段1: 项目基础定义生成"""

    async def generate(self, course_topic: str, course_overview: str,
                      age_group: str, duration: str, ai_tools: str) -> dict:
        """生成项目基础定义"""

        system_prompt = """你是一位资深的PBL（项目式学习）课程设计专家。
你的任务是根据用户提供的课程信息,生成项目基础定义,包括:
1. 驱动性问题（Driving Question）
2. 项目定义
3. 最终公开成果

输出要求:
- 使用Markdown格式
- 驱动性问题要有开放性和吸引力
- 项目定义要清晰具体
- 最终成果要可执行且符合年龄段"""

        user_prompt = f"""请为以下课程生成项目基础定义:

**课程主题**: {course_topic}
**课程概述**: {course_overview}
**年龄段**: {age_group}
**课程时长**: {duration}
**核心AI工具**: {ai_tools}

请生成:
1. 一个吸引人的驱动性问题
2. 清晰的项目定义(3-5句话)
3. 具体的最终公开成果描述

使用Markdown格式输出,分段清晰。"""

        try:
            start_time = time.time()

            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=settings.agent1_model or settings.openai_model,
                max_tokens=1500,
                temperature=0.7,
                timeout=30
            )

            generation_time = time.time() - start_time

            if not response["success"]:
                return {
                    "success": False,
                    "error": response.get("error", "AI生成失败"),
                    "generation_time": generation_time
                }

            return {
                "success": True,
                "content": response["content"],
                "generation_time": generation_time,
                "token_usage": response.get("token_usage", {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stage1Agent异常: {str(e)}",
                "generation_time": 0
            }


class Stage2Agent:
    """阶段2: 评估框架设计"""

    async def generate(self, course_topic: str, age_group: str, duration: str,
                      driving_question: str, project_definition: str,
                      final_deliverable: str) -> dict:
        """基于阶段1结果生成评估框架"""

        system_prompt = """你是一位资深的教育评估专家。
你的任务是根据已确定的项目基础,设计评估框架,包括:
1. 评估量规（Rubric）
2. 评估标准

评估要关注:
- 硬技能（技术能力）
- 软技能（协作、创造力等）
- 过程评估和成果评估相结合"""

        user_prompt = f"""请为以下项目设计评估框架:

**课程主题**: {course_topic}
**年龄段**: {age_group}
**课程时长**: {duration}

**驱动性问题**: {driving_question}

**项目定义**: {project_definition}

**最终成果**: {final_deliverable}

请设计:
1. 详细的评估量规(包含多个评估维度)
2. 具体的评估标准和打分规则

使用Markdown表格格式输出量规,确保清晰易懂。"""

        try:
            start_time = time.time()

            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=settings.agent2_model or settings.openai_model,
                max_tokens=2000,
                temperature=0.7,
                timeout=60
            )

            generation_time = time.time() - start_time

            if not response["success"]:
                return {
                    "success": False,
                    "error": response.get("error", "AI生成失败"),
                    "generation_time": generation_time
                }

            return {
                "success": True,
                "content": response["content"],
                "generation_time": generation_time,
                "token_usage": response.get("token_usage", {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stage2Agent异常: {str(e)}",
                "generation_time": 0
            }


class Stage3Agent:
    """阶段3: 学习蓝图生成"""

    async def generate(self, course_topic: str, age_group: str, duration: str,
                      ai_tools: str, driving_question: str, project_definition: str,
                      final_deliverable: str, evaluation_framework: str) -> dict:
        """基于阶段1和阶段2结果生成学习蓝图"""

        system_prompt = """你是一位资深的PBL课程设计师。
你的任务是根据已确定的项目基础和评估框架,生成详细的逐日教学计划。

计划要包括:
1. 每日活动安排
2. 教学目标
3. AI工具使用方式
4. 所需材料清单"""

        user_prompt = f"""请为以下项目生成详细的学习蓝图:

**课程主题**: {course_topic}
**年龄段**: {age_group}
**课程时长**: {duration}
**核心AI工具**: {ai_tools}

**驱动性问题**: {driving_question}

**项目定义**: {project_definition}

**最终成果**: {final_deliverable}

**评估框架**:
{evaluation_framework}

请生成:
1. 逐日详细教学计划(Day 1, Day 2, ...)
2. 每日的活动、目标、AI工具应用
3. 所需材料和资源清单

使用Markdown格式,结构清晰。"""

        try:
            start_time = time.time()

            response = await openai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=settings.agent3_model or settings.openai_model,
                max_tokens=3000,
                temperature=0.7,
                timeout=120
            )

            generation_time = time.time() - start_time

            if not response["success"]:
                return {
                    "success": False,
                    "error": response.get("error", "AI生成失败"),
                    "generation_time": generation_time
                }

            return {
                "success": True,
                "content": response["content"],
                "generation_time": generation_time,
                "token_usage": response.get("token_usage", {})
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stage3Agent异常: {str(e)}",
                "generation_time": 0
            }