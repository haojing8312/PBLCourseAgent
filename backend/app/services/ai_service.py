"""
AI服务 - 封装OpenAI API调用
"""
import asyncio
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings


class AIService:
    """AI服务类，处理与LLM的交互"""

    def __init__(self):
        """初始化AI服务"""
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行聊天完成请求

        Args:
            messages: 对话消息列表
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）

        Returns:
            包含响应和元数据的字典
        """
        try:
            # 构建消息列表
            conversation_messages = []

            # 添加系统提示词
            if system_prompt:
                conversation_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                # 默认PBL课程设计助手系统提示词
                default_system_prompt = """你是一个专业的PBL（项目式学习）课程设计AI助手。你的职责是：

1. 帮助教师设计高质量的PBL课程
2. 提供驱动性问题和学习目标建议
3. 规划项目时间线和学习活动
4. 设计评估框架和标准
5. 生成详细的教学蓝图

请始终以专业、友好、实用的方式回答问题，提供具体可操作的建议。
回答要条理清晰，使用合适的格式（如项目符号、编号列表等）。
当用户提供课程主题时，要深入分析并提供全面的设计方案。"""

                conversation_messages.append({
                    "role": "system",
                    "content": default_system_prompt
                })

            # 添加对话消息
            conversation_messages.extend(messages)

            # 设置参数
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens

            print(f"🤖 调用AI模型: {self.model}")
            print(f"📝 消息数量: {len(conversation_messages)}")

            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=conversation_messages,
                temperature=temp,
                max_tokens=max_tok,
            )

            # 提取响应内容
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content

                return {
                    "success": True,
                    "content": content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason
                }
            else:
                return {
                    "success": False,
                    "error": "No response choices returned from API"
                }

        except Exception as e:
            print(f"❌ AI服务调用失败: {str(e)}")
            return {
                "success": False,
                "error": f"AI服务错误: {str(e)}"
            }

    async def generate_pbl_course_suggestion(self, user_message: str) -> Dict[str, Any]:
        """
        专门为PBL课程设计生成建议

        Args:
            user_message: 用户输入的消息

        Returns:
            AI生成的课程设计建议
        """
        messages = [{
            "role": "user",
            "content": user_message
        }]

        return await self.chat_completion(messages)

    async def continue_conversation(
        self,
        conversation_history: List[Dict[str, str]],
        new_message: str
    ) -> Dict[str, Any]:
        """
        继续多轮对话

        Args:
            conversation_history: 之前的对话历史
            new_message: 新的用户消息

        Returns:
            AI响应
        """
        # 添加新消息到历史
        messages = conversation_history + [{
            "role": "user",
            "content": new_message
        }]

        return await self.chat_completion(messages)


# 全局AI服务实例
ai_service = AIService()