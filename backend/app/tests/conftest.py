"""
Pytest配置和共享fixtures
包括sentence-transformers模型配置用于语义相似度测试
"""
import pytest
import logging
from typing import Generator
import sys
import os

# 添加backend目录到Python路径
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import Base, engine, SessionLocal
from app.models.course_project import CourseProject

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ========== 数据库Fixtures ==========


@pytest.fixture(scope="session")
def db_engine():
    """
    创建测试数据库引擎（session级别，整个测试会话共享）
    """
    # 使用内存SQLite数据库进行测试
    from sqlalchemy import create_engine

    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # 创建所有表
    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    # 测试结束后清理
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    创建测试数据库会话（function级别，每个测试函数独立）
    """
    from sqlalchemy.orm import sessionmaker

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestSessionLocal()

    yield session

    # 测试结束后回滚和清理
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def sample_course(db_session):
    """
    创建示例课程项目
    """
    course = CourseProject(
        title="测试课程",
        subject="计算机科学",
        grade_level="高中",
        duration_weeks=12,
        description="这是一个测试课程",
        conversation_history=[],
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)

    yield course

    # 清理（会话回滚会自动处理）


# ========== Sentence Transformers Fixtures ==========


@pytest.fixture(scope="session")
def sentence_transformer_model():
    """
    加载sentence-transformers模型（session级别，避免重复加载）
    用于语义相似度测试
    """
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading sentence-transformers model for testing...")
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Model loaded successfully")
        return model

    except ImportError:
        logger.warning(
            "sentence-transformers not installed. Semantic tests will be skipped. "
            "Install with: uv add sentence-transformers"
        )
        pytest.skip("sentence-transformers not installed")

    except Exception as e:
        logger.error(f"Error loading sentence-transformers model: {e}")
        pytest.skip(f"Failed to load model: {e}")


@pytest.fixture(scope="session")
def semantic_similarity_function(sentence_transformer_model):
    """
    提供语义相似度计算函数
    """
    from sentence_transformers import util

    def compute_similarity(text1: str, text2: str) -> float:
        """
        计算两段文本的语义相似度

        Returns:
            float: 相似度分数 (0-1)
        """
        embeddings = sentence_transformer_model.encode(
            [text1, text2], convert_to_tensor=True
        )
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        return float(similarity.item())

    return compute_similarity


# ========== 黄金标准测试数据 ==========


@pytest.fixture(scope="session")
def golden_standard_v3():
    """
    加载黄金标准V3测试数据
    """
    import json
    from pathlib import Path

    golden_path = (
        Path(__file__).parent
        / "golden_standards"
        / "golden_standard_v3.json"
    )

    if not golden_path.exists():
        logger.warning(f"Golden standard V3 file not found: {golden_path}")
        pytest.skip("Golden standard V3 file not found")

    with open(golden_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


# ========== AI服务Mock ==========


@pytest.fixture
def mock_ai_response():
    """
    Mock AI响应（用于不需要真实AI调用的测试）
    """

    class MockAIResponse:
        def __init__(self, content: str, success: bool = True):
            self.content = content
            self.success = success
            self.error = None if success else "Mock error"

    def create_mock(content: str = "Mock AI response", success: bool = True):
        return MockAIResponse(content, success)

    return create_mock


# ========== 环境变量 ==========


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """
    设置测试环境变量
    """
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["PBL_AI_API_KEY"] = "test-key"
    os.environ["PBL_AI_MODEL"] = "test-model"


# ========== 语义相似度阈值常量 ==========

# UbD元素验证的语义相似度阈值
SEMANTIC_SIMILARITY_THRESHOLD = 0.80  # 80%以上视为高质量

# 黄金标准匹配阈值
GOLDEN_STANDARD_THRESHOLD = 0.75  # 75%以上视为符合黄金标准


# ========== Pytest配置 ==========


def pytest_configure(config):
    """
    Pytest配置钩子
    """
    # 添加自定义markers
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "semantic: mark test as semantic similarity test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "golden: mark test as golden standard validation")


def pytest_collection_modifyitems(config, items):
    """
    修改测试收集
    自动为某些测试添加markers
    """
    for item in items:
        # 为包含"semantic"的测试添加semantic marker
        if "semantic" in item.nodeid.lower():
            item.add_marker(pytest.mark.semantic)

        # 为包含"golden"的测试添加golden marker
        if "golden" in item.nodeid.lower():
            item.add_marker(pytest.mark.golden)
