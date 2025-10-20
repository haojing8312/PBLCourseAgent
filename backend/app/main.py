"""
FastAPI主应用程序
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="PBLCourseAgent",
        description="AI-Powered PBL Course Designer with Visual Task-Driven Canvas | 基于AI的项目式学习课程设计助手",
        version="2.0.0-alpha",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 配置CORS - 直接指定端口以确保生效
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:5173",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router, prefix="/api/v1")

    # V3 API路由 - 工作流和课程管理
    from app.api.v1.generate import router as workflow_router
    from app.api.v1.course import router as course_router

    app.include_router(workflow_router)  # 已包含/api/v1前缀
    app.include_router(course_router)    # 已包含/api/v1/courses前缀

    return app


app = create_app()


@app.get("/health")
async def health_check():
    """健康检查端点"""
    from app.models.schemas import HealthCheck
    return HealthCheck()