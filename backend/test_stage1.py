"""
直接测试Stage1Agent
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

async def test_stage1():
    try:
        print("🔍 开始测试Stage1Agent...")

        from app.agents.stage_agents import Stage1Agent

        agent = Stage1Agent()

        result = await agent.generate(
            course_topic="AI绘画创作",
            course_overview="学习使用Midjourney创作艺术作品",
            age_group="12-15岁",
            duration="4天",
            ai_tools="Midjourney"
        )

        print(f"\n✅ 测试完成")
        print(f"成功: {result.get('success')}")
        print(f"生成时间: {result.get('generation_time', 0):.2f}秒")

        if result.get('success'):
            print(f"\n📝 生成内容预览:")
            content = result.get('content', '')
            print(content[:500] if len(content) > 500 else content)
        else:
            print(f"\n❌ 错误: {result.get('error')}")

    except Exception as e:
        print(f"\n💥 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stage1())