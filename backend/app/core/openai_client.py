"""
OpenAI客户端管理
"""
import time
import asyncio
from typing import Any, Dict
from openai import AsyncOpenAI
from app.core.config import settings


class OpenAIClient:
    """OpenAI客户端封装类"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        生成AI响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            model: 模型名称，如不指定使用配置中的默认模型
            max_tokens: 最大令牌数，如不指定使用配置中的默认值
            temperature: 温度参数，如不指定使用配置中的默认值
            timeout: 超时时间（秒）

        Returns:
            包含响应内容和元数据的字典
        """
        start_time = time.time()

        # 使用配置中的默认值
        model = model or settings.openai_model
        max_tokens = max_tokens or settings.openai_max_tokens
        temperature = temperature if temperature is not None else settings.openai_temperature

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 使用asyncio.wait_for设置超时
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                ),
                timeout=timeout
            )

            end_time = time.time()
            response_time = end_time - start_time

            return {
                "content": response.choices[0].message.content,
                "response_time": response_time,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "model": response.model,
                "success": True,
            }

        except asyncio.TimeoutError:
            return {
                "content": None,
                "response_time": timeout,
                "error": f"Request timeout after {timeout} seconds",
                "success": False,
            }
        except Exception as e:
            end_time = time.time()
            return {
                "content": None,
                "response_time": end_time - start_time,
                "error": str(e),
                "success": False,
            }


# 全局客户端实例
openai_client = OpenAIClient()