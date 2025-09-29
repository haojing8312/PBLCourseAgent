"""
主应用测试
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_api_status():
    """测试API状态端点"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Service is running"
    assert data["data"]["status"] == "healthy"


def test_generate_course_endpoint():
    """测试课程生成端点"""
    test_input = {
        "course_topic": "AI乐队制作人",
        "course_overview": "学生将扮演一个乐队制作人的角色",
        "age_group": "13-15岁",
        "duration": "2天",
        "ai_tools": "Suno (AI音乐), Runway (AI视频)"
    }

    response = client.post("/api/v1/generate", json=test_input)
    assert response.status_code == 200
    data = response.json()
    # 注意：这个测试可能会失败，因为需要真实的OpenAI API密钥
    # 在没有API密钥的情况下，应该返回错误
    assert "success" in data