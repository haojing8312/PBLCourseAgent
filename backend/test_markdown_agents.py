"""
测试 Markdown Agents
"""
import asyncio
from app.agents import (
    ProjectFoundationAgentV3,
    AssessmentFrameworkAgentV3,
    LearningBlueprintAgentV3,
)


async def test_agents():
    """测试三个Agent的Markdown输出"""

    # 1. 测试 Agent 1
    print("=== 测试 Agent 1 (Project Foundation) ===")
    agent1 = ProjectFoundationAgentV3()
    result1 = await agent1.generate(
        title="测试课程",
        subject="计算机科学",
        grade_level="高中",
        duration_weeks=12,
        description="一个测试课程"
    )

    if result1["success"]:
        print(f"✅ Agent 1 成功")
        print(f"   返回字段: {list(result1.keys())}")
        print(f"   有 'markdown' 字段: {'markdown' in result1}")
        print(f"   Markdown 长度: {len(result1.get('markdown', ''))} 字符")
    else:
        print(f"❌ Agent 1 失败: {result1.get('error')}")
        return

    stage_one_markdown = result1["markdown"]

    # 2. 测试 Agent 2
    print("\n=== 测试 Agent 2 (Assessment Framework) ===")
    agent2 = AssessmentFrameworkAgentV3()
    result2 = await agent2.generate(
        stage_one_data=stage_one_markdown,
        course_info={
            "title": "测试课程",
            "duration_weeks": 12
        }
    )

    if result2["success"]:
        print(f"✅ Agent 2 成功")
        print(f"   返回字段: {list(result2.keys())}")
        print(f"   有 'markdown' 字段: {'markdown' in result2}")
        print(f"   Markdown 长度: {len(result2.get('markdown', ''))} 字符")
    else:
        print(f"❌ Agent 2 失败: {result2.get('error')}")
        return

    stage_two_markdown = result2["markdown"]

    # 3. 测试 Agent 3
    print("\n=== 测试 Agent 3 (Learning Blueprint) ===")
    agent3 = LearningBlueprintAgentV3()
    result3 = await agent3.generate(
        stage_one_data=stage_one_markdown,
        stage_two_data=stage_two_markdown,
        course_info={
            "title": "测试课程",
            "duration_weeks": 12
        }
    )

    if result3["success"]:
        print(f"✅ Agent 3 成功")
        print(f"   返回字段: {list(result3.keys())}")
        print(f"   有 'markdown' 字段: {'markdown' in result3}")
        print(f"   Markdown 长度: {len(result3.get('markdown', ''))} 字符")
    else:
        print(f"❌ Agent 3 失败: {result3.get('error')}")
        return

    print("\n=== 所有测试通过 ✅ ===")


if __name__ == "__main__":
    asyncio.run(test_agents())
