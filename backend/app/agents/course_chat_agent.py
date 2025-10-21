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
        stage_one_data: Optional[str] = None,
        stage_two_data: Optional[str] = None,
        stage_three_data: Optional[str] = None,
    ) -> str:
        """
        构建系统提示词（V3版本 - 接收 Markdown 字符串）

        根据当前阶段和已有数据，动态构建上下文

        Args:
            stage_one_data: Stage One Markdown 字符串
            stage_two_data: Stage Two Markdown 字符串
            stage_three_data: Stage Three Markdown 字符串
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

        # 添加已有Stage数据作为上下文（Markdown格式）
        if stage_one_data:
            prompt += f"""
已完成 Stage 1 数据（预期学习结果 - Markdown格式）：
{stage_one_data}

"""

        if stage_two_data:
            prompt += f"""
已完成 Stage 2 数据（评估框架 - Markdown格式）：
{stage_two_data}

"""

        if stage_three_data:
            prompt += f"""
已完成 Stage 3 数据（学习蓝图 - Markdown格式）：
{stage_three_data}

"""

        prompt += """
请基于以上上下文回答用户的问题。如果用户询问当前课程的内容，请参考上述数据。

【重要】当用户明确要求修改课程方案时，你需要触发重新生成：
1. 在回复的**第一行**添加特殊标记：[REGENERATE:STAGE_X:修改说明]
   - X是阶段编号（1/2/3）
   - 修改说明是对用户需求的简洁总结（不超过50字）

2. 然后在第二行开始正常回复用户，解释你的修改思路

判断标准（非常重要！）：

【必须触发REGENERATE的场景】：
1. 用户明确说"修改方案"、"重新设计方案"、"调整方案"
2. 涉及课程时长/课时调整（如"改成2周"、"课时改为8节"、"压缩到X周"）
3. 涉及整体结构调整（如"合并阶段"、"增加活动"、"简化评估"）
4. 使用命令式语气："把XX改成YY"、"调整XX为YY"、"帮我修改XX"
5. 涉及核心要素的修改（学习目标、评估框架、学习活动等）

【不需要触发REGENERATE的场景】：
1. 纯咨询性问题："为什么这样设计？"、"什么是UbD？"
2. 纯询问性问题："可以怎么改进？"、"有什么建议？"
3. 纯讨论性话题："如果改成XX会怎样？"、"这个方案适合XX吗？"

【判断技巧】：
- 关键词："修改方案"、"重新生成"、"调整课时"、"改成"、"压缩到" → 一定REGENERATE
- 关键句式："帮我XXX"、"把XXX改成YYY"、"XXX改为YYY" → 一定REGENERATE
- 如果不确定用户是想"获得建议"还是"执行修改"，倾向于触发REGENERATE

示例1（必须触发 - 课时调整）：
用户："帮我修改一下方案，我们的课时一共是2周8课时，要修改方案适合这个时长"
你的回复：
[REGENERATE:STAGE_3:调整课程时长从12周压缩至2周8课时]
好的，我将重新生成适合2周8课时的方案。这需要对原有的12周方案进行大幅压缩和精简...

示例2（必须触发 - 目标修改）：
用户："把学习目标改成培养批判性思维"
你的回复：
[REGENERATE:STAGE_1:将学习目标重点调整为培养批判性思维能力]
好的，我将重新生成Stage 1，将学习目标的重点调整为培养批判性思维。这是一个很好的方向，因为...

示例3（必须触发 - 评估调整）：
用户："调整评估量规，增加更多案例"
你的回复：
[REGENERATE:STAGE_2:优化评估量规并增加案例说明]
好的，我将重新生成Stage 2的评估框架，增加更多具体案例...

示例4（不触发 - 纯咨询）：
用户："为什么要这样设计学习目标？"
你的回复：
这样设计学习目标是基于UbD的理论...（直接回答，不加标记）

示例5（不触发 - 纯讨论）：
用户："这个方案适合初中生吗？"
你的回复：
这个方案在设计时考虑了初中生的认知水平...（直接回答，不加标记）

注意：标记必须独占第一行，格式严格遵守，否则系统无法识别。
"""

        return prompt

    async def chat_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        current_step: int = 1,
        course_info: Optional[Dict[str, Any]] = None,
        stage_one_data: Optional[str] = None,
        stage_two_data: Optional[str] = None,
        stage_three_data: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        流式对话（SSE）- V3版本（接收 Markdown 字符串）

        Args:
            user_message: 用户消息
            conversation_history: 历史对话（不包含当前消息）
            current_step: 当前步骤
            course_info: 课程基本信息
            stage_one_data: Stage 1 Markdown字符串
            stage_two_data: Stage 2 Markdown字符串
            stage_three_data: Stage 3 Markdown字符串

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
        stage_one_data: Optional[str] = None,
        stage_two_data: Optional[str] = None,
        stage_three_data: Optional[str] = None,
    ) -> str:
        """
        非流式对话（一次性返回完整回复）- V3版本（接收 Markdown 字符串）

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
        from app.core.config import settings

        _chat_agent_instance = CourseChatAgent(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            temperature=0.7,  # 对话模式使用0.7
        )

        logger.info("[CourseChatAgent] Initialized chat agent singleton")

    return _chat_agent_instance
