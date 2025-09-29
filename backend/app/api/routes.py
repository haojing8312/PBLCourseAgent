"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProjectInput, ApiResponse
from app.core.workflow_service import workflow_service

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