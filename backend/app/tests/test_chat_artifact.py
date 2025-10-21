"""
测试Chat API的Artifact事件功能

验证：
1. 正则表达式能否正确识别REGENERATE标记
2. artifact事件的格式是否正确
"""
import re
import pytest


class TestArtifactDetection:
    """测试Artifact标记检测逻辑"""

    def test_regenerate_pattern_basic(self):
        """测试基本的REGENERATE标记匹配"""
        response = "[REGENERATE:STAGE_1:将学习目标调整为培养批判性思维]\n好的，我将重新生成..."

        # 使用与chat.py相同的正则表达式
        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'
        match = re.match(pattern, response)

        assert match is not None, "应该匹配到REGENERATE标记"
        assert match.group(1) == "1", "应该提取到stage编号1"
        assert match.group(2).strip() == "将学习目标调整为培养批判性思维", "应该提取到修改说明"

    def test_regenerate_pattern_stage2(self):
        """测试Stage 2的REGENERATE标记"""
        response = "[REGENERATE:STAGE_2:优化评估量规使其更加具体可操作]\n我将调整评估框架..."

        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'
        match = re.match(pattern, response)

        assert match is not None
        assert match.group(1) == "2"
        assert "优化评估量规" in match.group(2)

    def test_regenerate_pattern_stage3(self):
        """测试Stage 3的REGENERATE标记"""
        response = "[REGENERATE:STAGE_3:增加更多实践活动]\n好的..."

        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'
        match = re.match(pattern, response)

        assert match is not None
        assert match.group(1) == "3"

    def test_no_regenerate_pattern(self):
        """测试普通对话（不包含REGENERATE标记）"""
        response = "这样设计学习目标是基于UbD的理论，因为..."

        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'
        match = re.match(pattern, response)

        assert match is None, "普通对话不应该匹配到REGENERATE标记"

    def test_regenerate_with_special_characters(self):
        """测试包含特殊字符的修改说明"""
        response = "[REGENERATE:STAGE_1:将目标改为\"培养创新思维\"和批判性分析能力]\n开始修改..."

        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'
        match = re.match(pattern, response)

        assert match is not None
        instructions = match.group(2).strip()
        assert "创新思维" in instructions
        assert "批判性分析" in instructions

    def test_regenerate_pattern_must_be_first_line(self):
        """测试REGENERATE标记必须在第一行"""
        # 正确格式：标记在第一行
        correct_response = "[REGENERATE:STAGE_1:修改说明]\n后续内容..."
        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'
        match = re.match(pattern, correct_response)
        assert match is not None, "第一行的标记应该被匹配"

        # 错误格式：标记不在第一行（match会失败因为用的是re.match而不是re.search）
        wrong_response = "一些前置文字\n[REGENERATE:STAGE_1:修改说明]\n后续内容..."
        match = re.match(pattern, wrong_response)
        assert match is None, "不在第一行的标记不应该被匹配（re.match从开头匹配）"

    def test_extract_stage_and_instructions(self):
        """测试提取stage和instructions的完整逻辑"""
        test_cases = [
            {
                "response": "[REGENERATE:STAGE_1:调整学习目标]\n内容...",
                "expected_stage": 1,
                "expected_instructions": "调整学习目标"
            },
            {
                "response": "[REGENERATE:STAGE_2:优化评估框架，增加更多案例]\n内容...",
                "expected_stage": 2,
                "expected_instructions": "优化评估框架，增加更多案例"
            },
            {
                "response": "[REGENERATE:STAGE_3:重新设计学习活动，增加小组合作环节]\n内容...",
                "expected_stage": 3,
                "expected_instructions": "重新设计学习活动，增加小组合作环节"
            }
        ]

        pattern = r'\[REGENERATE:STAGE_(\d+):(.*?)\]'

        for case in test_cases:
            match = re.match(pattern, case["response"])
            assert match is not None, f"应该匹配到: {case['response']}"

            stage = int(match.group(1))
            instructions = match.group(2).strip()

            assert stage == case["expected_stage"], f"Stage应该是{case['expected_stage']}"
            assert instructions == case["expected_instructions"], f"Instructions应该是{case['expected_instructions']}"


class TestArtifactEventFormat:
    """测试Artifact事件的JSON格式"""

    def test_artifact_event_json_format(self):
        """测试artifact事件的JSON格式是否正确"""
        import json

        artifact_event = {
            'type': 'artifact',
            'action': 'regenerate',
            'stage': 1,
            'instructions': '将学习目标调整为培养批判性思维'
        }

        # 序列化为JSON
        json_str = json.dumps(artifact_event, ensure_ascii=False)

        # 反序列化验证
        parsed = json.loads(json_str)

        assert parsed['type'] == 'artifact'
        assert parsed['action'] == 'regenerate'
        assert parsed['stage'] == 1
        assert parsed['instructions'] == '将学习目标调整为培养批判性思维'

    def test_sse_format(self):
        """测试SSE格式是否正确"""
        import json

        artifact_event = {
            'type': 'artifact',
            'action': 'regenerate',
            'stage': 2,
            'instructions': '优化评估量规'
        }

        # 构建SSE格式
        sse_line = f"data: {json.dumps(artifact_event, ensure_ascii=False)}\n\n"

        # 验证格式
        assert sse_line.startswith("data: ")
        assert sse_line.endswith("\n\n")

        # 提取JSON部分
        json_part = sse_line[6:-2]  # 去掉 "data: " 和 "\n\n"
        parsed = json.loads(json_part)

        assert parsed['type'] == 'artifact'
        assert parsed['stage'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
