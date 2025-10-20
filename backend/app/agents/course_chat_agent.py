"""
Course Chat Agent - 课程设计专业对话Agent

对标ChatGPT的专业AI助手，专注于UbD-PBL课程设计咨询。

功能：
- 支持流式响应（SSE）
- 理解课程上下文（已生成的Stage数据）
- 提供专业的UbD/PBL建议
- 解释设计理由
- 协助修改和完善
"""
import json
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class CourseChatAgent:
    """
    课程设计对话Agent

    专业能力：
    - UbD逆向设计理论
    - PBL项目式学习方法
    - 课程设计最佳实践
    - 教学评估框架
    """

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
        temperature: float = 0.7,
    ):
        """
        初始化Chat Agent

        Args:
            api_key: OpenAI API密钥
            model: 模型名称
            base_url: API基础URL
            temperature: 生成温度（0.7适合对话）
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
        self.temperature = temperature

    def _build_system_prompt(
        self,
        current_step: int,
        course_info: Optional[Dict[str, Any]] = None,
        stage_one_data: Optional[Dict[str, Any]] = None,
        stage_two_data: Optional[Dict[str, Any]] = None,
        stage_three_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        构建系统提示词

        根据当前阶段和已有数据，动态构建上下文
        """
        # 基础身份定义
        prompt = """你是一位资深的课程设计专家，精通UbD（为理解而设计）逆向设计理论和PBL（项目式学习）教学法。

你的角色：
- 帮助教师设计高质量的UbD-PBL课程
- 解释设计理由和教育学原理
- 提供具体、可操作的建议
- 对不合理的设计提出改进意见

对话风格：
- 专业但友好
- 提供具体案例
- 引用教育理论
- 给出可行建议

"""

        # 添加课程信息上下文
        if course_info:
            prompt += f"""
当前课程信息：
- 课程名称：{course_info.get('title', 'N/A')}
- 学科领域：{course_info.get('subject', 'N/A')}
- 年级水平：{course_info.get('grade_level', 'N/A')}
- 课程时长：{course_info.get('duration_weeks', 'N/A')}周
- 课程简介：{course_info.get('description', 'N/A')}

"""

        # 添加当前阶段说明
        stage_names = {
            1: "Stage 1: 确定预期学习结果 (Goals/Understandings/Questions/Knowledge/Skills)",
            2: "Stage 2: 设计评估证据 (驱动性问题/表现性任务/评估量规)",
            3: "Stage 3: 规划PBL学习体验 (学习活动/WHERETO原则)"
        }

        prompt += f"""
当前阶段：{stage_names.get(current_step, f'Stage {current_step}')}

"""

        # 添加已有Stage数据作为上下文
        if stage_one_data:
            prompt += f"""
已完成 Stage 1 数据（预期学习结果）：
{json.dumps(stage_one_data, ensure_ascii=False, indent=2)}

"""

        if stage_two_data:
            prompt += f"""
已完成 Stage 2 数据（评估框架）：
{json.dumps(stage_two_data, ensure_ascii=False, indent=2)}

"""

        if stage_three_data:
            prompt += f"""
已完成 Stage 3 数据（学习蓝图）：
{json.dumps(stage_three_data, ensure_ascii=False, indent=2)}

"""

        prompt += """
请基于以上上下文回答用户的问题。如果用户询问当前课程的内容，请参考上述数据。
如果用户要求修改某个部分，请给出具体的修改建议并解释理由。
"""

        return prompt

    async def chat_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        current_step: int = 1,
        course_info: Optional[Dict[str, Any]] = None,
        stage_one_data: Optional[Dict[str, Any]] = None,
        stage_two_data: Optional[Dict[str, Any]] = None,
        stage_three_data: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        流式对话（SSE）

        Args:
            user_message: 用户消息
            conversation_history: 历史对话（不包含当前消息）
            current_step: 当前步骤
            course_info: 课程基本信息
            stage_one_data: Stage 1数据
            stage_two_data: Stage 2数据
            stage_three_data: Stage 3数据

        Yields:
            str: AI回复的文本片段（流式输出）
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(
                current_step=current_step,
                course_info=course_info,
                stage_one_data=stage_one_data,
                stage_two_data=stage_two_data,
                stage_three_data=stage_three_data,
            )

            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # 添加历史对话（最多保留最近10轮）
            recent_history = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
            for msg in recent_history:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })

            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })

            logger.info(f"[CourseChatAgent] Starting stream chat, message count: {len(messages)}")

            # 流式调用LLM
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=True,
            )

            # 流式输出
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content

        except Exception as e:
            logger.error(f"[CourseChatAgent] Stream chat error: {e}", exc_info=True)
            error_msg = f"抱歉，遇到了一些技术问题：{str(e)}"
            yield error_msg

    async def chat_non_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        current_step: int = 1,
        course_info: Optional[Dict[str, Any]] = None,
        stage_one_data: Optional[Dict[str, Any]] = None,
        stage_two_data: Optional[Dict[str, Any]] = None,
        stage_three_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        非流式对话（一次性返回完整回复）

        主要用于测试或特殊场景
        """
        try:
            system_prompt = self._build_system_prompt(
                current_step=current_step,
                course_info=course_info,
                stage_one_data=stage_one_data,
                stage_two_data=stage_two_data,
                stage_three_data=stage_three_data,
            )

            messages = [{"role": "system", "content": system_prompt}]

            recent_history = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
            for msg in recent_history:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({"role": msg['role'], "content": msg['content']})

            messages.append({"role": "user", "content": user_message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=False,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"[CourseChatAgent] Non-stream chat error: {e}", exc_info=True)
            return f"抱歉，遇到了一些技术问题：{str(e)}"


# 单例模式
_chat_agent_instance: Optional[CourseChatAgent] = None


def get_chat_agent() -> CourseChatAgent:
    """
    获取Chat Agent单例
    """
    global _chat_agent_instance

    if _chat_agent_instance is None:
        from app.core.config import get_settings
        settings = get_settings()

        _chat_agent_instance = CourseChatAgent(
            api_key=settings.AI_API_KEY,
            model=settings.AI_MODEL,
            base_url=settings.AI_BASE_URL,
            temperature=0.7,  # 对话模式使用0.7
        )

        logger.info("[CourseChatAgent] Initialized chat agent singleton")

    return _chat_agent_instance
