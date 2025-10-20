"""
UbD元素验证服务
使用语义相似度检查U (Understandings) 是否是真正的抽象理解，而非知识点
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# 优秀的U示例（作为语义基准）
GOOD_U_EXAMPLES = [
    "理解AI技术的双刃剑特性：它既能带来便利，也可能引发风险",
    "认识到数据质量直接决定AI模型的有效性和公平性",
    "意识到编程语言是表达思想的工具，而不仅仅是记忆语法",
    "理解AI并非魔法，而是基于大量数据和数学模型的模式识别系统",
    "认识到技术创新的速度与伦理审查之间存在平衡的必要性",
    "理解复杂系统通过简单规则的迭代产生涌现行为",
    "意识到算法决策中的偏见反映了训练数据中的社会偏见",
]

# 错误的U示例（实际上是K或S）
BAD_U_EXAMPLES = [
    "掌握Python编程基础语法",
    "了解机器学习的基本算法",
    "学会使用ChatGPT进行代码生成",
    "知道监督学习和非监督学习的区别",
    "掌握提示工程的技巧",
]


class ValidationService:
    """
    UbD元素验证服务
    """

    def __init__(self):
        """
        初始化验证服务
        延迟加载sentence-transformers模型（仅在需要时加载）
        """
        self.model = None
        self._model_loaded = False

    def _load_model(self):
        """
        延迟加载sentence-transformers模型
        """
        if self._model_loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer, util

            logger.info("Loading sentence-transformers model...")
            # 使用轻量级中文模型
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            self.util = util
            self._model_loaded = True
            logger.info("Sentence-transformers model loaded successfully")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Validation scores will be set to 0.5 (neutral). "
                "Install with: uv add sentence-transformers"
            )
            self._model_loaded = False
        except Exception as e:
            logger.error(f"Error loading sentence-transformers model: {e}")
            self._model_loaded = False

    def validate_understanding(self, u_text: str) -> Dict[str, Any]:
        """
        验证一个U (Understanding) 是否是真正的抽象理解

        Args:
            u_text: 待验证的理解陈述

        Returns:
            {
                "is_valid": bool,  # 是否通过验证（score >= 0.7）
                "score": float,  # 验证分数 (0-1)
                "explanation": str,  # 验证说明
                "suggestions": List[str]  # 改进建议
            }
        """
        self._load_model()

        # 如果模型未加载，返回中性分数
        if not self._model_loaded or self.model is None:
            return {
                "is_valid": True,  # 不阻止流程
                "score": 0.5,  # 中性分数
                "explanation": "语义验证服务不可用，使用默认评分",
                "suggestions": [],
            }

        try:
            # 计算与优秀U示例的相似度
            good_embeddings = self.model.encode(
                GOOD_U_EXAMPLES, convert_to_tensor=True
            )
            bad_embeddings = self.model.encode(
                BAD_U_EXAMPLES, convert_to_tensor=True
            )
            u_embedding = self.model.encode([u_text], convert_to_tensor=True)

            # 与优秀示例的相似度
            good_similarities = self.util.pytorch_cos_sim(u_embedding, good_embeddings)[
                0
            ]
            avg_good_sim = float(good_similarities.mean())

            # 与错误示例的相似度
            bad_similarities = self.util.pytorch_cos_sim(u_embedding, bad_embeddings)[0]
            avg_bad_sim = float(bad_similarities.mean())

            # 计算验证分数：优秀相似度高 & 错误相似度低 = 高分
            score = max(0.0, min(1.0, avg_good_sim * 0.7 + (1 - avg_bad_sim) * 0.3))

            # 判断是否通过
            is_valid = score >= 0.7

            # 生成解释和建议
            explanation = self._generate_explanation(
                score, avg_good_sim, avg_bad_sim, u_text
            )
            suggestions = (
                self._generate_suggestions(u_text) if not is_valid else []
            )

            return {
                "is_valid": is_valid,
                "score": round(score, 2),
                "explanation": explanation,
                "suggestions": suggestions,
            }

        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return {
                "is_valid": True,  # 出错时不阻止流程
                "score": 0.5,
                "explanation": f"验证过程出错: {str(e)}",
                "suggestions": [],
            }

    def _generate_explanation(
        self, score: float, good_sim: float, bad_sim: float, u_text: str
    ) -> str:
        """
        生成验证说明
        """
        if score >= 0.85:
            return f"✅ 优秀的理解陈述！语义与抽象理解高度相似（{score:.2f}），是真正的big idea。"
        elif score >= 0.7:
            return f"✓ 合格的理解陈述。语义评分为{score:.2f}，符合抽象理解的特征。"
        elif score >= 0.5:
            return f"⚠️ 理解陈述可能过于具体。语义评分为{score:.2f}，建议增强抽象性和可迁移性。"
        else:
            return f"❌ 理解陈述可能是知识点或技能。语义评分为{score:.2f}，请检查是否符合U的定义（抽象观念而非具体知识）。"

    def _generate_suggestions(self, u_text: str) -> List[str]:
        """
        生成改进建议
        """
        suggestions = []

        # 检查常见问题
        if any(
            verb in u_text
            for verb in ["掌握", "学会", "了解", "知道", "熟悉", "记住"]
        ):
            suggestions.append(
                "避免使用'掌握'、'学会'、'了解'等动词。U应该使用'理解'、'认识到'、'意识到'等抽象动词。"
            )

        if any(
            tool in u_text
            for tool in [
                "Python",
                "ChatGPT",
                "API",
                "代码",
                "函数",
                "变量",
                "算法",
            ]
        ):
            suggestions.append(
                "U中出现了具体的工具或技术术语。尝试提取背后的普遍原理，而非具体实现。例如：'理解编程语言是表达思想的工具'而非'掌握Python语法'。"
            )

        if len(u_text) < 15:
            suggestions.append("U的描述过短。优秀的U通常需要20-50字来表达一个完整的抽象观念。")

        if "如何" in u_text or "怎样" in u_text:
            suggestions.append(
                "U不应该是'如何做'的问题，那是技能S。U应该是'为什么'或'是什么'的深层洞察。"
            )

        if not suggestions:
            suggestions.append(
                "尝试问自己：'学生在5年后还会记得这个洞察吗？'如果答案是否定的，说明这可能不是真正的U。"
            )

        return suggestions

    def validate_stage_one(self, stage_one_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证完整的Stage One数据

        Args:
            stage_one_data: {
                "goals": [...],
                "understandings": [...],  # 需要验证
                "questions": [...],
                "knowledge": [...],
                "skills": [...]
            }

        Returns:
            {
                "overall_valid": bool,
                "understandings_validation": [
                    {"text": "...", "is_valid": bool, "score": float, ...}
                ],
                "avg_score": float,
                "warnings": List[str]
            }
        """
        understandings = stage_one_data.get("understandings", [])
        validations = []
        warnings = []

        for u in understandings:
            u_text = u.get("text", "")
            validation = self.validate_understanding(u_text)
            validations.append({"text": u_text, **validation})

            if not validation["is_valid"]:
                warnings.append(f"理解陈述 '{u_text[:30]}...' 的验证分数较低")

        avg_score = (
            sum(v["score"] for v in validations) / len(validations)
            if validations
            else 0.0
        )

        overall_valid = avg_score >= 0.7

        return {
            "overall_valid": overall_valid,
            "understandings_validation": validations,
            "avg_score": round(avg_score, 2),
            "warnings": warnings,
        }


# 全局单例
_validation_service = None


def get_validation_service() -> ValidationService:
    """
    获取验证服务单例
    """
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service
