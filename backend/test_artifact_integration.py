"""
集成测试：验证Artifact事件的完整流程

测试流程：
1. 创建一个测试课程
2. 生成Stage 1
3. 通过Chat API发送修改请求
4. 验证是否收到artifact事件
"""
import asyncio
import json
from app.core.database import SessionLocal
from app.models.course_project import CourseProject
from app.api.v1.chat import stream_chat_response


async def test_artifact_event():
    """测试artifact事件的生成"""
    print("=" * 60)
    print("开始集成测试：Artifact事件")
    print("=" * 60)

    # 1. 创建测试课程
    db = SessionLocal()
    try:
        # 创建课程
        course = CourseProject(
            title="测试课程",
            subject="计算机科学",
            grade_level="大学",
            duration_weeks=12,
            description="用于测试artifact事件的课程",
            stage_one_data="# Stage 1\n学习目标：掌握Python基础"
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        print(f"✅ 创建测试课程 ID={course.id}")

        # 2. 准备对话请求
        user_message = "把学习目标改成培养批判性思维"
        conversation_history = []
        current_step = 1

        course_info = {
            "title": course.title,
            "subject": course.subject,
            "grade_level": course.grade_level,
            "duration_weeks": course.duration_weeks,
            "description": course.description
        }

        print(f"📝 用户消息: {user_message}")

        # 3. 调用stream_chat_response
        print("🔄 调用stream_chat_response...")

        artifact_detected = False
        artifact_data = None
        full_response = ""

        async for event_str in stream_chat_response(
            user_message=user_message,
            conversation_history=conversation_history,
            current_step=current_step,
            course_info=course_info,
            stage_one_data=course.stage_one_data,
            stage_two_data=None,
            stage_three_data=None
        ):
            # 解析SSE事件
            if event_str.startswith("data: "):
                json_str = event_str[6:].strip()
                if json_str:
                    try:
                        event = json.loads(json_str)
                        print(f"   事件类型: {event.get('type')}")

                        if event['type'] == 'chunk':
                            full_response += event.get('content', '')

                        elif event['type'] == 'artifact':
                            artifact_detected = True
                            artifact_data = event
                            print(f"   🎯 检测到artifact事件!")
                            print(f"      - action: {event.get('action')}")
                            print(f"      - stage: {event.get('stage')}")
                            print(f"      - instructions: {event.get('instructions')}")

                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  JSON解析失败: {e}")

        # 4. 验证结果
        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)

        print(f"\n完整AI回复:\n{full_response[:200]}...")

        if artifact_detected:
            print("\n✅ 测试通过：成功检测到artifact事件")
            print(f"   Stage: {artifact_data.get('stage')}")
            print(f"   Instructions: {artifact_data.get('instructions')}")
            return True
        else:
            print("\n❌ 测试失败：未检测到artifact事件")
            print("   可能原因：")
            print("   1. AI未正确识别修改意图")
            print("   2. AI回复中未包含REGENERATE标记")
            print(f"   3. AI完整回复: {full_response}")
            return False

    finally:
        # 清理测试数据
        db.query(CourseProject).filter(CourseProject.id == course.id).delete()
        db.commit()
        db.close()
        print("\n🧹 清理测试数据完成")


if __name__ == "__main__":
    result = asyncio.run(test_artifact_event())
    exit(0 if result else 1)
