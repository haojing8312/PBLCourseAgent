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

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/health")
async def health_check():
    """健康检查端点"""
    from app.models.schemas import HealthCheck
    return HealthCheck()