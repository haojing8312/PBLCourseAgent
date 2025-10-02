"""
OpenAI流式客户端 - 用于实时显示生成进度
"""
import time
import asyncio
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.core.config import settings


class OpenAIStreamingClient:
    """OpenAI流式客户端封装类"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = 120
    ) -> AsyncGenerator[str, None]:
        """
        流式生成AI响应

        Yields:
            str: 逐个token的内容片段
        """
        model = model or settings.openai_model
        max_tokens = max_tokens or settings.openai_max_tokens
        temperature = temperature if temperature is not None else settings.openai_temperature

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 流式请求
            stream = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True,  # 开启流式响应
                ),
                timeout=timeout
            )

            # 逐块返回内容
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except asyncio.TimeoutError:
            yield f"\n\n[ERROR] Request timeout after {timeout} seconds"
        except Exception as e:
            yield f"\n\n[ERROR] {str(e)}"


# 全局流式客户端实例
openai_streaming_client = OpenAIStreamingClient()