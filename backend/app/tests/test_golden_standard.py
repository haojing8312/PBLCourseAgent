"""
黄金标准案例测试
使用PRD中定义的黄金标准案例来验证系统输出质量
"""
import pytest
import json
from app.core.workflow_service import workflow_service
from app.models.schemas import ProjectInput


class TestGoldenStandard:
    """黄金标准测试类"""

    @pytest.fixture
    def golden_input(self):
        """黄金标准案例输入"""
        return ProjectInput(
            course_topic="AI乐队制作人",
            course_overview="学生将扮演一个乐队制作人的角色，使用AI工具为一首预设的歌词创作旋律、编曲，并制作一个简单的歌词MV。",
            age_group="13-15岁",
            duration="2天",
            ai_tools="Suno (AI音乐), Runway (AI视频), Canva (平面设计)"
        )

    @pytest.fixture
    def expected_elements(self):
        """黄金标准案例中应该包含的关键元素"""
        return {
            "project_foundation": {
                "driving_question_keywords": ["制作人", "AI工具", "歌曲", "视听"],
                "public_product_keywords": ["歌曲", "MV", "发布会"],
                "required_components": ["歌曲", "视频", "封面"],
                "cover_page_elements": ["courseTitle", "tagline", "ageGroup", "duration", "aiTools"]
            },
            "assessment_framework": {
                "min_rubric_dimensions": 3,
                "required_rubric_keywords": ["音乐", "创意", "技术"],
                "min_checkpoints": 2,
                "checkpoint_keywords": ["试听", "检查", "预览"]
            },
            "learning_blueprint": {
                "required_prep_materials": ["电脑", "软件", "设备"],
                "required_skills": ["Suno", "Runway", "Canva"],
                "min_timeline_activities": 5,
                "activity_keywords": ["音乐", "视频", "设计"]
            }
        }

    def calculate_quality_score(self, result_data: dict, expected: dict) -> dict:
        """
        计算质量得分

        Args:
            result_data: 系统生成的结果
            expected: 期望的元素

        Returns:
            包含各维度得分的字典
        """
        scores = {
            "project_foundation": 0,
            "assessment_framework": 0,
            "learning_blueprint": 0,
            "overall": 0
        }

        # 评估项目基础定义
        if "project_foundation" in result_data:
            foundation = result_data["project_foundation"]
            foundation_score = 0

            # 检查驱动性问题
            if "drivingQuestion" in foundation:
                question = foundation["drivingQuestion"].lower()
                keyword_matches = sum(1 for keyword in expected["project_foundation"]["driving_question_keywords"]
                                    if keyword in question)
                foundation_score += (keyword_matches / len(expected["project_foundation"]["driving_question_keywords"])) * 25

            # 检查公开成果
            if "publicProduct" in foundation:
                product = json.dumps(foundation["publicProduct"], ensure_ascii=False).lower()
                keyword_matches = sum(1 for keyword in expected["project_foundation"]["public_product_keywords"]
                                    if keyword in product)
                foundation_score += (keyword_matches / len(expected["project_foundation"]["public_product_keywords"])) * 25

            # 检查封面页元素
            if "coverPage" in foundation:
                cover_page = foundation["coverPage"]
                element_matches = sum(1 for element in expected["project_foundation"]["cover_page_elements"]
                                    if element in cover_page)
                foundation_score += (element_matches / len(expected["project_foundation"]["cover_page_elements"])) * 25

            # 检查学习目标
            if "learningObjectives" in foundation:
                objectives = json.dumps(foundation["learningObjectives"], ensure_ascii=False).lower()
                if "硬技能" in objectives or "hardskills" in objectives or "hard skills" in objectives:
                    foundation_score += 12.5
                if "软技能" in objectives or "softskills" in objectives or "soft skills" in objectives:
                    foundation_score += 12.5

            scores["project_foundation"] = min(foundation_score, 100)

        # 评估评估框架
        if "assessment_framework" in result_data:
            assessment = result_data["assessment_framework"]
            assessment_score = 0

            # 检查量规维度数量
            if "summativeRubric" in assessment:
                rubric = assessment["summativeRubric"]
                if len(rubric) >= expected["assessment_framework"]["min_rubric_dimensions"]:
                    assessment_score += 25

                # 检查关键词
                rubric_text = json.dumps(rubric, ensure_ascii=False).lower()
                keyword_matches = sum(1 for keyword in expected["assessment_framework"]["required_rubric_keywords"]
                                    if keyword in rubric_text)
                assessment_score += (keyword_matches / len(expected["assessment_framework"]["required_rubric_keywords"])) * 25

            # 检查检查点
            if "formativeCheckpoints" in assessment:
                checkpoints = assessment["formativeCheckpoints"]
                if len(checkpoints) >= expected["assessment_framework"]["min_checkpoints"]:
                    assessment_score += 25

                # 检查检查点关键词
                checkpoint_text = json.dumps(checkpoints, ensure_ascii=False).lower()
                keyword_matches = sum(1 for keyword in expected["assessment_framework"]["checkpoint_keywords"]
                                    if keyword in checkpoint_text)
                assessment_score += (keyword_matches / len(expected["assessment_framework"]["checkpoint_keywords"])) * 25

            scores["assessment_framework"] = min(assessment_score, 100)

        # 评估学习蓝图
        if "learning_blueprint" in result_data:
            blueprint = result_data["learning_blueprint"]
            blueprint_score = 0

            # 检查教师准备
            if "teacherPrep" in blueprint:
                prep = blueprint["teacherPrep"]
                if "materialList" in prep and len(prep["materialList"]) >= 3:
                    blueprint_score += 20

                if "skillPrerequisites" in prep and len(prep["skillPrerequisites"]) >= 2:
                    blueprint_score += 20

                # 检查关键技能
                prep_text = json.dumps(prep, ensure_ascii=False).lower()
                skill_matches = sum(1 for skill in expected["learning_blueprint"]["required_skills"]
                                  if skill.lower() in prep_text)
                blueprint_score += (skill_matches / len(expected["learning_blueprint"]["required_skills"])) * 20

            # 检查时间线
            if "timeline" in blueprint:
                timeline = blueprint["timeline"]
                if len(timeline) >= expected["learning_blueprint"]["min_timeline_activities"]:
                    blueprint_score += 20

                # 检查活动关键词
                timeline_text = json.dumps(timeline, ensure_ascii=False).lower()
                keyword_matches = sum(1 for keyword in expected["learning_blueprint"]["activity_keywords"]
                                    if keyword in timeline_text)
                blueprint_score += (keyword_matches / len(expected["learning_blueprint"]["activity_keywords"])) * 20

            scores["learning_blueprint"] = min(blueprint_score, 100)

        # 计算总分
        scores["overall"] = (scores["project_foundation"] +
                           scores["assessment_framework"] +
                           scores["learning_blueprint"]) / 3

        return scores

    @pytest.mark.asyncio
    @pytest.mark.slow  # 标记为慢速测试，需要真实API调用
    async def test_golden_standard_quality(self, golden_input, expected_elements):
        """
        测试黄金标准案例的质量
        注意：这个测试需要真实的OpenAI API密钥才能运行
        """
        try:
            # 执行完整工作流程
            result = await workflow_service.execute_full_workflow(golden_input)

            # 验证基本成功
            assert result["success"] is True, f"工作流程执行失败: {result.get('message', 'Unknown error')}"
            assert "data" in result

            # 验证数据结构完整性
            data = result["data"]
            assert "project_foundation" in data
            assert "assessment_framework" in data
            assert "learning_blueprint" in data
            assert "metadata" in data

            # 计算质量得分
            quality_scores = self.calculate_quality_score(data, expected_elements)

            print(f"\n📊 黄金标准案例质量评估结果:")
            print(f"   项目基础定义: {quality_scores['project_foundation']:.1f}/100")
            print(f"   评估框架设计: {quality_scores['assessment_framework']:.1f}/100")
            print(f"   学习蓝图生成: {quality_scores['learning_blueprint']:.1f}/100")
            print(f"   总体质量得分: {quality_scores['overall']:.1f}/100")

            # 验证性能指标
            metadata = data["metadata"]
            print(f"\n⏱️  性能指标:")
            print(f"   总耗时: {metadata['total_time']:.2f}秒")
            print(f"   Agent 1: {metadata['agent_times'].get('agent1', 0):.2f}秒")
            print(f"   Agent 2: {metadata['agent_times'].get('agent2', 0):.2f}秒")
            print(f"   Agent 3: {metadata['agent_times'].get('agent3', 0):.2f}秒")

            # 断言质量标准
            assert quality_scores["overall"] >= 80.0, f"质量得分 {quality_scores['overall']:.1f} 低于80%的目标阈值"

            # 断言性能标准
            assert metadata["total_time"] < 90, f"总耗时 {metadata['total_time']:.2f}秒 超过90秒的目标"

            print(f"\n✅ 黄金标准案例测试通过！")

        except Exception as e:
            if "API key" in str(e) or "openai" in str(e).lower():
                pytest.skip(f"跳过黄金标准测试，需要OpenAI API密钥: {str(e)}")
            else:
                raise e

    def test_quality_score_calculation(self, expected_elements):
        """测试质量得分计算逻辑"""
        # 模拟一个完美的结果
        mock_result = {
            "project_foundation": {
                "drivingQuestion": "作为一名新生代的音乐制作人，我们如何仅凭AI工具就能创作出一首能触动人心的歌曲？",
                "publicProduct": {
                    "description": "一首完整的歌曲及其MV，将举办发布会展示"
                },
                "learningObjectives": {
                    "hardSkills": ["音乐技能"],
                    "softSkills": ["创意能力"]
                },
                "coverPage": {
                    "courseTitle": "AI乐队制作人",
                    "tagline": "标语",
                    "ageGroup": "13-15岁",
                    "duration": "2天",
                    "aiTools": "AI工具"
                }
            },
            "assessment_framework": {
                "summativeRubric": [
                    {"dimension": "音乐创意技术能力"},
                    {"dimension": "第二维度"},
                    {"dimension": "第三维度"}
                ],
                "formativeCheckpoints": [
                    {"name": "音乐试听检查"},
                    {"name": "视频预览检查"}
                ]
            },
            "learning_blueprint": {
                "teacherPrep": {
                    "materialList": ["电脑", "软件", "设备", "其他"],
                    "skillPrerequisites": ["Suno技能", "Runway技能", "Canva技能"]
                },
                "timeline": [
                    {"activityTitle": "音乐创作"},
                    {"activityTitle": "视频制作"},
                    {"activityTitle": "设计工作"},
                    {"activityTitle": "活动4"},
                    {"activityTitle": "活动5"}
                ]
            }
        }

        scores = self.calculate_quality_score(mock_result, expected_elements)

        # 验证得分范围
        for component, score in scores.items():
            assert 0 <= score <= 100, f"{component} 得分 {score} 不在有效范围内"

        # 对于完美匹配的案例，得分应该很高
        assert scores["overall"] >= 80, f"完美案例的总得分 {scores['overall']} 应该高于80%"