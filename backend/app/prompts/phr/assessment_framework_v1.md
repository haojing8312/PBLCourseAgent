# Prompt History Record: AssessmentFrameworkAgent v1.0

## Meta Information
- **Version**: v1.0
- **Created**: 2025-01-15 (估计，基于项目初始化时间)
- **Last Modified**: 2025-01-20
- **Agent Name**: Genesis Two (AssessmentFrameworkAgent)
- **Model**: deepseek-chat (or configured model)
- **Model Parameters**:
  - Temperature: 0.6
  - Max Tokens: 2500
  - Timeout: 25秒
- **Performance Metrics** (基于初始测试):
  - Average Response Time: 22秒
  - Success Rate: ~92%
  - Quality Score: 8.2/10 (基于UbD框架符合度评估)

---

## System Prompt

```
# ROLE & CONTEXT
You are "Genesis Two", a meticulous curriculum evaluator with expertise in educational assessment and PBL evaluation frameworks. Your task is to create a comprehensive assessment framework based on the provided project foundation. The framework must be practical for a non-expert teacher to use.

# INSTRUCTION
Based on the project foundation JSON, generate an assessment framework. The output MUST be a valid JSON object following the specified schema. The rubric descriptions should be clear, positive, and action-oriented.

# SCHEMA
{
  "summativeRubric": [
    {
      "dimension": "The skill or quality being measured (e.g., '创意构思').",
      "level_1_desc": "Description for '新手' level.",
      "level_2_desc": "Description for '学徒' level.",
      "level_3_desc": "Description for '工匠' level.",
      "level_4_desc": "Description for '大师' level."
    }
  ],
  "formativeCheckpoints": [
    {
      "name": "The name of the checkpoint (e.g., '创意概念审核').",
      "triggerTime": "When this check happens (e.g., '上午结束前').",
      "purpose": "What the teacher should check for."
    }
  ]
}

# GUIDELINES FOR RUBRIC CREATION
- Create 3-4 rubric dimensions that cover both technical skills and soft skills
- Each dimension should have 4 levels: 新手, 学徒, 工匠, 大师
- Descriptions should be specific and observable behaviors
- Focus on what students CAN do at each level, not what they lack
- Include technical AI tool usage and creative/collaboration skills
- Make descriptions age-appropriate for the target audience

# GUIDELINES FOR CHECKPOINTS
- Create 2-4 formative checkpoints throughout the project timeline
- Checkpoints should be at logical stopping points in the workflow
- Each checkpoint should have a clear purpose for quality assurance
- Include specific timing that makes sense for the project duration
- Focus on preventing problems rather than just catching them

# OUTPUT REQUIREMENTS
- All text must be in Chinese
- Rubric dimensions should align with the learning objectives from the project foundation
- Checkpoints should align with the anticipated workflow and timeline
- Descriptions should be clear enough for a non-expert teacher to apply consistently
```

---

## User Prompt Template

输入格式（由Agent代码动态构建）：

```json
{
  "drivingQuestion": "...",
  "publicProduct": {...},
  "learningObjectives": {
    "hardSkills": [...],
    "softSkills": [...]
  },
  "coverPage": {...}
}
```

用户提示词：

```
# PROJECT FOUNDATION
{上述Agent 1的完整输出JSON}

请基于以上项目基础信息，生成符合Schema要求的评估框架JSON。确保：
1. 总结性量规（summativeRubric）涵盖学习目标中的硬技能和软技能
2. 每个维度的4个等级描述具体、可观测、积极正面
3. 形成性检查点（formativeCheckpoints）在关键节点设置，有明确的质量保证目的
4. 评估标准适合目标年龄段，便于非专业教师操作

直接返回JSON格式，不要任何额外说明。
```

---

## Guidelines for Use

### 适用场景
- 基于ProjectFoundation生成UbD评估框架
- 输入要求：Agent 1的完整输出（包含学习目标、年龄段、时长等）
- 输出：包含总结性量规和形成性检查点的JSON

### 关键设计原则

1. **总结性量规（Summative Rubric）设计**

   **维度选择**：
   - 3-4个维度
   - 必须覆盖硬技能（AI工具使用）和软技能（21世纪素养）
   - 与Agent 1的learningObjectives严格对齐

   **四级描述**：
   - **新手**：基础水平，完成基本任务
   - **学徒**：理解核心概念，能够独立操作
   - **工匠**：熟练应用，有创新元素
   - **大师**：卓越表现，超越预期

   **描述原则**：
   - ✅ 聚焦"能做什么"（Can-do statements）
   - ✅ 使用可观测的行为动词
   - ✅ 积极正面的语言
   - ❌ 避免"不能"、"缺乏"等否定词

   **示例**（AI绘画课）：
   ```json
   {
     "dimension": "AI工具创意应用",
     "level_1_desc": "能使用Midjourney生成基础图像，理解简单的提示词结构",
     "level_2_desc": "能调整提示词参数生成符合主题的图像，理解提示词与输出的关系",
     "level_3_desc": "能创造性地组合多个提示词元素，生成具有个人风格的作品",
     "level_4_desc": "能系统性地测试和优化提示词，创作出主题鲜明、技术精湛的系列作品"
   }
   ```

2. **形成性检查点（Formative Checkpoints）设计**

   **数量**：2-4个，取决于课程时长
   - 3小时课程：2个检查点
   - 1天课程：3个检查点
   - 2天课程：4个检查点

   **时机选择**：
   - 在关键技能习得后
   - 在阶段性成果产出时
   - 在可能出错的环节前

   **目的明确性**：
   - 不是"检查进度"，而是"确保质量"
   - 应该包含具体的观察点
   - 教师能快速判断是否达标

   **示例**（3小时AI绘画课）：
   ```json
   [
     {
       "name": "提示词理解检查",
       "triggerTime": "开始后30分钟",
       "purpose": "确认学生理解基础提示词结构，能生成至少1张符合要求的图像。检查点：每位学生展示1张作品并解释提示词"
     },
     {
       "name": "创意方向确认",
       "triggerTime": "上午结束前",
       "purpose": "确保学生的创意方向明确且可执行。检查点：学生口头描述最终作品构想，教师给予反馈"
     }
   ]
   ```

### 温度和Token设置理由

- **Temperature: 0.6**
  - 比Agent 1略低（0.7 → 0.6）
  - 评估框架需要更高的一致性和结构性
  - 同时保留一定灵活性以适应不同主题

- **Max Tokens: 2500**
  - 量规描述需要详细清晰
  - 4个维度 × 4个等级 = 16段描述
  - 加上检查点说明，需要更多Token
  - 实测平均使用约1800-2200 tokens

---

## Change Log

### v1.0 (2025-01-15)
- **描述**: 初始版本，基于UbD框架设计
- **特性**:
  - 四级量规设计（新手→学徒→工匠→大师）
  - 形成性检查点集成
  - 积极正面的描述语言
  - 对齐Agent 1的学习目标
- **测试结果**:
  - 在5个测试案例上平均质量评分8.2/10
  - 量规与学习目标对齐度95%
  - 检查点实用性评分8.5/10

---

## Known Issues

### 1. 量规维度有时与学习目标不完全对齐
**现象**: 偶尔（~8%）生成的量规维度不能完全覆盖Agent 1中的所有学习目标

**原因**:
- Agent 1可能生成5-6个学习目标
- Agent 2只生成3-4个量规维度
- LLM在合并相似目标时可能遗漏某些

**影响**: 评估不够全面

**解决方案**:
- 在User Prompt中强调"确保涵盖所有学习目标"
- 或在Agent代码中添加后处理验证

### 2. 检查点时机描述有时过于模糊
**现象**: 如"中途"、"过程中"等模糊的时间描述

**期望**: "开始后30分钟"、"上午结束前"等具体时间

**改进方向**:
- 在Guidelines中增加时间描述示例
- 要求必须包含具体时间或明确的里程碑事件

### 3. 大师级描述有时过于理想化
**现象**: 四级描述中，"大师"级别的要求有时超出年龄段合理预期

**示例**: 小学生课程中要求"展现专业级别的艺术理解"

**影响**: 降低量规的实用性

**改进方向**: v1.1中增加年龄适宜性检查

---

## Testing Notes

### 测试案例

**案例1: 小学AI绘画课（对应Agent 1案例1）**
- 输入: Agent 1的输出（包含3个硬技能，2个软技能）
- 输出质量: 8.5/10
- 生成的量规维度:
  1. AI工具创意应用
  2. 艺术表达能力
  3. 团队协作与分享
- 检查点数量: 2个
- 评价: 优秀，维度与学习目标完全对齐，检查点时机合理

**案例2: 中学环保项目**
- 输入: Agent 1的输出（包含4个硬技能，3个软技能）
- 输出质量: 7.5/10
- 问题: 量规只生成了3个维度，未能覆盖所有7个学习目标
- 检查点: 3个，时机合理但目的描述略显宽泛
- 改进建议: 明确要求维度数量匹配目标复杂度

**案例3: 高中商业策划**
- 输出质量: 8.5/10
- 生成的量规维度:
  1. AI辅助研究与分析
  2. 商业计划完整性
  3. 创新思维与可行性
  4. 演讲与说服力
- 检查点: 4个（对应2天课程）
- 评价: 很好，维度全面，检查点分布均匀

### 性能测试

- **平均响应时间**: 22秒 (范围: 16-32秒)
- **Token使用**: 平均1950 tokens/请求
- **成功率**: 92% (25次测试中23次成功)
- **失败原因**:
  - 1次JSON格式错误（缺少逗号）
  - 1次超时（API波动）

### 优化建议

1. **增强学习目标覆盖率**
   - 在System Prompt中强调"维度必须覆盖所有学习目标"
   - 允许生成4-5个维度以适应复杂项目

2. **改进检查点时间描述**
   - 提供时间描述模板：
     - 短期课程（3小时）："开始后X分钟"、"结束前X分钟"
     - 全天课程："上午结束前"、"午休后"、"下午X点"
     - 多天课程："第X天上午"、"第X天结束前"

3. **年龄适宜性校准**
   - 根据coverPage.ageGroup调整量规描述的复杂度
   - 小学：具体行为描述，避免抽象概念
   - 中学：平衡行为和思维过程
   - 高中：可包含元认知和批判性思维

4. **增加量规示例**
   - 在System Prompt中提供2-3个优秀量规示例
   - 覆盖不同年龄段和主题

---

## Related Files

- **Agent Implementation**: `backend/app/agents/assessment_framework_agent.py`
- **Test File**: `backend/app/tests/test_assessment_framework_agent.py`
- **Configuration**: `backend/app/core/config.py` (agent2_model, agent2_timeout)
- **Depends On**: Agent 1输出 (`project_foundation_v1.md`)

---

## UbD Framework Compliance

本Prompt设计严格遵循Understanding by Design框架：

1. **逆向设计第二阶段**：确定合适的评估证据
   - 总结性评估（Summative）：最终成果的量规
   - 形成性评估（Formative）：过程中的检查点

2. **评估一致性**：
   - 量规维度直接对应学习目标
   - 检查点预设在关键学习节点

3. **教师可操作性**：
   - 描述清晰，非专业教师也能理解
   - 检查点有具体的观察指南

---

## Version Upgrade Path

### 计划中的v1.1改进
- [ ] 增强学习目标全覆盖检查
- [ ] 优化检查点时间描述规范
- [ ] 添加年龄适宜性校准逻辑
- [ ] 提供优秀量规示例库

### 潜在的v2.0方向
- [ ] 支持多种评估哲学（除UbD外，如PBL Works量规）
- [ ] 生成学生自评和互评版本
- [ ] 集成数字化评分工具建议（如Google Forms模板）
