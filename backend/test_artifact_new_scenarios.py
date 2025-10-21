"""
集成测试：验证新增的Artifact场景识别能力

特别测试：
1. 课时调整场景："帮我修改一下方案，课时改成2周8课时"
2. 其他边界场景
"""
import asyncio
import json
from app.core.database import SessionLocal
from app.models.course_project import CourseProject
from app.api.v1.chat import stream_chat_response


async def test_course_duration_adjustment():
    """
    测试场景1：课时调整

    用户说："帮我修改一下方案，我们的课时一共是2周8课时，要修改方案适合这个时长"

    预期：应该触发artifact事件
    """
    print("=" * 60)
    print("测试场景1：课时调整识别")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 创建测试课程
        course = CourseProject(
            title="测试课程 - 12周版本",
            subject="计算机科学",
            grade_level="初中",
            duration_weeks=12,
            description="原始的12周课程方案",
            stage_three_data="# Stage 3\n当前是12周的学习蓝图..."
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        print(f"✅ 创建测试课程 ID={course.id}")

        # 用户请求
        user_message = "帮我修改一下方案，我们的课时一共是2周8课时，要修改方案适合这个时长"

        course_info = {
            "title": course.title,
            "subject": course.subject,
            "grade_level": course.grade_level,
            "duration_weeks": course.duration_weeks,
            "description": course.description
        }

        print(f"📝 用户消息: {user_message}")
        print("🔄 调用stream_chat_response...")

        artifact_detected = False
        artifact_data = None
        full_response = ""

        async for event_str in stream_chat_response(
            user_message=user_message,
            conversation_history=[],
            current_step=3,  # 学习蓝图在Stage 3
            course_info=course_info,
            stage_one_data=None,
            stage_two_data=None,
            stage_three_data=course.stage_three_data
        ):
            if event_str.startswith("data: "):
                json_str = event_str[6:].strip()
                if json_str:
                    try:
                        event = json.loads(json_str)

                        if event['type'] == 'chunk':
                            full_response += event.get('content', '')

                        elif event['type'] == 'artifact':
                            artifact_detected = True
                            artifact_data = event
                            print(f"   🎯 检测到artifact事件!")
                            print(f"      - action: {event.get('action')}")
                            print(f"      - stage: {event.get('stage')}")
                            print(f"      - instructions: {event.get('instructions')}")

                    except json.JSONDecodeError:
                        pass

        # 验证结果
        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)

        print(f"\nAI回复摘要（前200字符）:\n{full_response[:200]}...")

        if artifact_detected:
            print("\n✅ 测试通过：成功识别课时调整请求")
            print(f"   Stage: {artifact_data.get('stage')}")
            print(f"   Instructions: {artifact_data.get('instructions')}")

            # 验证stage是否正确（应该是3，因为课时调整影响学习蓝图）
            if artifact_data.get('stage') == 3:
                print("   ✅ Stage识别正确（Stage 3）")
            else:
                print(f"   ⚠️  Stage识别可能有问题（预期Stage 3，实际{artifact_data.get('stage')}）")

            return True
        else:
            print("\n❌ 测试失败：未检测到artifact事件")
            print("   AI将修改建议直接在对话中返回了")
            print(f"   AI完整回复（前500字符）: {full_response[:500]}")
            return False

    finally:
        # 清理测试数据
        db.query(CourseProject).filter(CourseProject.id == course.id).delete()
        db.commit()
        db.close()
        print("\n🧹 清理测试数据完成")


async def test_evaluation_adjustment():
    """
    测试场景2：评估框架调整

    用户说："调整评估量规，增加更多案例"

    预期：应该触发artifact事件
    """
    print("\n" + "=" * 60)
    print("测试场景2：评估框架调整识别")
    print("=" * 60)

    db = SessionLocal()
    try:
        course = CourseProject(
            title="测试课程",
            subject="计算机科学",
            grade_level="初中",
            duration_weeks=12,
            stage_two_data="# Stage 2\n当前的评估量规..."
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        user_message = "调整评估量规，增加更多案例"

        course_info = {
            "title": course.title,
            "subject": course.subject,
            "grade_level": course.grade_level,
            "duration_weeks": course.duration_weeks,
        }

        print(f"📝 用户消息: {user_message}")

        artifact_detected = False

        async for event_str in stream_chat_response(
            user_message=user_message,
            conversation_history=[],
            current_step=2,
            course_info=course_info,
            stage_one_data=None,
            stage_two_data=course.stage_two_data,
            stage_three_data=None
        ):
            if event_str.startswith("data: "):
                json_str = event_str[6:].strip()
                if json_str:
                    try:
                        event = json.loads(json_str)
                        if event['type'] == 'artifact':
                            artifact_detected = True
                            print(f"   🎯 检测到artifact事件!")
                    except json.JSONDecodeError:
                        pass

        if artifact_detected:
            print("   ✅ 测试通过：成功识别评估调整请求")
            return True
        else:
            print("   ❌ 测试失败：未检测到artifact事件")
            return False

    finally:
        db.query(CourseProject).filter(CourseProject.id == course.id).delete()
        db.commit()
        db.close()


async def test_pure_consultation():
    """
    测试场景3：纯咨询问题（不应触发）

    用户说："为什么要设计这么长的课时？"

    预期：不应该触发artifact事件
    """
    print("\n" + "=" * 60)
    print("测试场景3：纯咨询问题（不应触发）")
    print("=" * 60)

    db = SessionLocal()
    try:
        course = CourseProject(
            title="测试课程",
            subject="计算机科学",
            grade_level="初中",
            duration_weeks=12,
            stage_three_data="# Stage 3\n12周的学习蓝图..."
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        user_message = "为什么要设计这么长的课时？"

        course_info = {
            "title": course.title,
            "duration_weeks": course.duration_weeks,
        }

        print(f"📝 用户消息: {user_message}")

        artifact_detected = False

        async for event_str in stream_chat_response(
            user_message=user_message,
            conversation_history=[],
            current_step=3,
            course_info=course_info,
            stage_one_data=None,
            stage_two_data=None,
            stage_three_data=course.stage_three_data
        ):
            if event_str.startswith("data: "):
                json_str = event_str[6:].strip()
                if json_str:
                    try:
                        event = json.loads(json_str)
                        if event['type'] == 'artifact':
                            artifact_detected = True
                    except json.JSONDecodeError:
                        pass

        if not artifact_detected:
            print("   ✅ 测试通过：正确识别为咨询问题，未触发artifact")
            return True
        else:
            print("   ❌ 测试失败：误触发了artifact事件")
            return False

    finally:
        db.query(CourseProject).filter(CourseProject.id == course.id).delete()
        db.commit()
        db.close()


async def main():
    """运行所有测试"""
    print("\n")
    print("=" * 60)
    print("开始运行新场景集成测试")
    print("=" * 60)

    results = []

    # 测试1：课时调整（最重要）
    result1 = await test_course_duration_adjustment()
    results.append(("课时调整识别", result1))

    # 测试2：评估调整
    result2 = await test_evaluation_adjustment()
    results.append(("评估调整识别", result2))

    # 测试3：纯咨询（不应触发）
    result3 = await test_pure_consultation()
    results.append(("纯咨询识别", result3))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(r for _, r in results)

    if all_passed:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
