"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ProjectInput, ApiResponse, ChatMessage, ChatRequest,
    Stage1Input, Stage1Output, Stage2Input, Stage2Output,
    Stage3Input, Stage3Output
)
from app.core.workflow_service import workflow_service
from app.services.ai_service import ai_service
import time

router = APIRouter()


@router.post("/generate", response_model=ApiResponse)
async def generate_course(project_input: ProjectInput):
    """
    生成完整的PBL课程方案
    """
    try:
        print(f"📝 收到课程生成请求: {project_input.course_topic}")

        # 执行完整的工作流程
        result = await workflow_service.execute_full_workflow(project_input)

        if result["success"]:
            return ApiResponse(
                success=True,
                message=result["message"],
                data=result["data"]
            )
        else:
            return ApiResponse(
                success=False,
                message=result["message"],
                data=result.get("data"),
                error="; ".join(result.get("errors", []))
            )

    except Exception as e:
        print(f"❌ 课程生成异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """获取服务状态"""
    return ApiResponse(
        success=True,
        message="Service is running",
        data={"status": "healthy"}
    )


@router.get("/health")
async def health_check():
    """健康检查 - 检查所有Agent状态"""
    try:
        health_result = await workflow_service.health_check()

        if health_result["success"]:
            return ApiResponse(
                success=True,
                message=health_result["message"],
                data=health_result["data"]
            )
        else:
            return ApiResponse(
                success=False,
                message=health_result["message"],
                data=health_result["data"]
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ApiResponse)
async def chat(chat_request: ChatRequest):
    """
    AI助手对话接口 - 真正的AI对话功能
    """
    try:
        print(f"💬 收到聊天消息: {chat_request.message}")

        # 调用AI服务进行真实对话
        ai_response = await ai_service.generate_pbl_course_suggestion(chat_request.message)

        if ai_response["success"]:
            # AI调用成功
            print(f"✅ AI响应成功，使用模型: {ai_response.get('model', 'unknown')}")
            print(f"📊 Token使用情况: {ai_response.get('usage', {})}")

            return ApiResponse(
                success=True,
                message="AI聊天响应成功",
                data={
                    "response": ai_response["content"],
                    "session_id": chat_request.session_id or "default",
                    "context": "pbl_course_design",
                    "ai_model": ai_response.get("model", "unknown"),
                    "token_usage": ai_response.get("usage", {}),
                    "finish_reason": ai_response.get("finish_reason", "unknown")
                }
            )
        else:
            # AI调用失败，直接返回错误，不提供降级回复
            error_message = ai_response.get('error', 'AI服务连接失败')
            print(f"❌ AI调用失败: {error_message}")

            return ApiResponse(
                success=False,
                message="AI服务调用失败",
                error=error_message,
                data={
                    "session_id": chat_request.session_id or "default",
                    "error_details": error_message
                }
            )

    except Exception as e:
        print(f"❌ 聊天处理异常: {str(e)}")

        # 直接返回系统错误，不提供降级回复
        return ApiResponse(
            success=False,
            message="系统处理异常",
            error=str(e),
            data={
                "session_id": chat_request.session_id or "default"
            }
        )


# ========== 分阶段生成API ==========

@router.post("/generate/stage1test")
async def generate_stage1_test(input_data: Stage1Input):
    """测试endpoint - 不使用response_model"""
    try:
        print(f"✅ [TEST] 收到请求: {input_data.course_topic}")

        from app.agents.stage_agents import Stage1Agent
        agent = Stage1Agent()

        result = await agent.generate(
            course_topic=input_data.course_topic,
            course_overview=input_data.course_overview,
            age_group=input_data.age_group,
            duration=input_data.duration,
            ai_tools=input_data.ai_tools
        )

        print(f"✅ [TEST] Agent返回: success={result.get('success')}")

        return {"test": "success", "agent_result": result}
    except Exception as e:
        print(f"❌ [TEST] 异常: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"test": "failed", "error": str(e)}


@router.post("/generate/stage1", response_model=ApiResponse)
async def generate_stage1(input_data: Stage1Input):
    """
    阶段1: 生成项目基础定义
    """
    try:
        print(f"🎯 [阶段1] 开始生成项目基础定义: {input_data.course_topic}")

        # 使用简化的Stage1Agent
        from app.agents.stage_agents import Stage1Agent
        agent = Stage1Agent()

        result = await agent.generate(
            course_topic=input_data.course_topic,
            course_overview=input_data.course_overview,
            age_group=input_data.age_group,
            duration=input_data.duration,
            ai_tools=input_data.ai_tools
        )

        if result["success"]:
            content = result["content"]

            # 简单提取关键信息（用户可以在前端编辑）
            driving_q = "请从下方内容中查看"
            proj_def = "请从下方内容中查看"
            final_del = "请从下方内容中查看"

            # 尝试提取（可选）
            if "驱动性问题" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "驱动性问题" in line and i + 1 < len(lines):
                        driving_q = lines[i + 1].strip()
                        break

            output = Stage1Output(
                driving_question=driving_q,
                project_definition=proj_def,
                final_deliverable=final_del,
                cover_page=f"# {input_data.course_topic}\n\n**年龄段**: {input_data.age_group}\n**时长**: {input_data.duration}",
                raw_content=content,
                generation_time=result["generation_time"]
            )

            print(f"✅ [阶段1] 生成完成，耗时 {result['generation_time']:.2f}秒")

            return ApiResponse(
                success=True,
                message=f"阶段1生成成功，耗时 {result['generation_time']:.2f}秒",
                data=output.dict()
            )
        else:
            print(f"❌ [阶段1] 生成失败: {result.get('error')}")
            return ApiResponse(
                success=False,
                message="阶段1生成失败",
                error=result.get("error", "Unknown error")
            )

    except Exception as e:
        print(f"❌ [阶段1] 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stage2", response_model=ApiResponse)
async def generate_stage2(input_data: Stage2Input):
    """
    阶段2: 基于阶段1结果生成评估框架
    """
    try:
        print(f"🎯 [阶段2] 开始生成评估框架")

        # 使用Stage2Agent
        from app.agents.stage_agents import Stage2Agent
        agent = Stage2Agent()

        result = await agent.generate(
            course_topic=input_data.course_topic,
            age_group=input_data.age_group,
            duration=input_data.duration,
            driving_question=input_data.driving_question,
            project_definition=input_data.project_definition,
            final_deliverable=input_data.final_deliverable
        )

        if result["success"]:
            content = result["content"]

            output = Stage2Output(
                rubric_markdown=content,
                evaluation_criteria="见上方量规",
                raw_content=content,
                generation_time=result["generation_time"]
            )

            print(f"✅ [阶段2] 生成完成，耗时 {result['generation_time']:.2f}秒")

            return ApiResponse(
                success=True,
                message=f"阶段2生成成功，耗时 {result['generation_time']:.2f}秒",
                data=output.dict()
            )
        else:
            print(f"❌ [阶段2] 生成失败: {result.get('error')}")
            return ApiResponse(
                success=False,
                message="阶段2生成失败",
                error=result.get("error", "Unknown error")
            )

    except Exception as e:
        print(f"❌ [阶段2] 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stage3", response_model=ApiResponse)
async def generate_stage3(input_data: Stage3Input):
    """
    阶段3: 基于阶段1和阶段2结果生成学习蓝图
    """
    try:
        print(f"🎯 [阶段3] 开始生成学习蓝图")

        # 使用Stage3Agent
        from app.agents.stage_agents import Stage3Agent
        agent = Stage3Agent()

        result = await agent.generate(
            course_topic=input_data.course_topic,
            age_group=input_data.age_group,
            duration=input_data.duration,
            ai_tools=input_data.ai_tools,
            driving_question=input_data.driving_question,
            project_definition=input_data.project_definition,
            final_deliverable=input_data.final_deliverable,
            evaluation_framework=input_data.rubric_markdown
        )

        if result["success"]:
            content = result["content"]

            output = Stage3Output(
                day_by_day_plan=content,
                activities_summary="见详细计划",
                materials_list="见详细计划",
                raw_content=content,
                generation_time=result["generation_time"]
            )

            print(f"✅ [阶段3] 生成完成，耗时 {result['generation_time']:.2f}秒")

            return ApiResponse(
                success=True,
                message=f"阶段3生成成功，耗时 {result['generation_time']:.2f}秒",
                data=output.dict()
            )
        else:
            print(f"❌ [阶段3] 生成失败: {result.get('error')}")
            return ApiResponse(
                success=False,
                message="阶段3生成失败",
                error=result.get("error", "Unknown error")
            )

    except Exception as e:
        print(f"❌ [阶段3] 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ========== 流式生成API (Server-Sent Events) ==========

from fastapi.responses import StreamingResponse
import json


async def generate_stage3_stream_content(input_data: Stage3Input):
    """生成Stage3的流式内容"""
    from app.core.openai_streaming import openai_streaming_client
    from app.core.config import settings

    system_prompt = """你是一位资深的PBL课程设计师。
你的任务是根据已确定的项目基础和评估框架,生成详细的逐日教学计划。

计划要包括:
1. 每日活动安排
2. 教学目标
3. AI工具使用方式
4. 所需材料清单"""

    user_prompt = f"""请为以下项目生成详细的学习蓝图:

**课程主题**: {input_data.course_topic}
**年龄段**: {input_data.age_group}
**课程时长**: {input_data.duration}
**核心AI工具**: {input_data.ai_tools}

**驱动性问题**: {input_data.driving_question}

**项目定义**: {input_data.project_definition}

**最终成果**: {input_data.final_deliverable}

**评估框架**:
{input_data.rubric_markdown}

请生成:
1. 逐日详细教学计划(Day 1, Day 2, ...)
2. 每日的活动、目标、AI工具应用
3. 所需材料和资源清单

使用Markdown格式,结构清晰。"""

    # 流式生成
    full_content = ""
    async for chunk in openai_streaming_client.generate_stream(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model=settings.agent3_model or settings.openai_model,
        max_tokens=3000,
        temperature=0.7,
        timeout=120
    ):
        full_content += chunk
        # 发送SSE格式数据
        yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"

    # 发送完成信号
    yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_content': full_content})}\n\n"


@router.post("/generate/stage3/stream")
async def generate_stage3_stream(input_data: Stage3Input):
    """
    阶段3: 流式生成学习蓝图 (Server-Sent Events)
    """
    print(f"🎯 [阶段3-流式] 开始生成学习蓝图")

    return StreamingResponse(
        generate_stage3_stream_content(input_data),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )