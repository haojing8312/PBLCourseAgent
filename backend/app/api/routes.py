"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProjectInput, ApiResponse, ChatMessage, ChatRequest
from app.core.workflow_service import workflow_service
from app.services.ai_service import ai_service

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