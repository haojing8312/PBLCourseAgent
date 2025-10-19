# Jaaz 改造方案：集成 UBD 课程设计 Agent

> **改造目标**: 在保留 Jaaz 原有图像/视频生成能力的基础上，新增 UBD（逆向设计）课程设计 Agent 群组，支持 PBL 课程方案自动生成与可视化
>
> **设计时间**: 2025-10-05
> **设计者**: Claude Code (Linus Mode)

---

## 📋 目录

1. [需求分析](#需求分析)
2. [现状分析](#现状分析)
3. [改造架构设计](#改造架构设计)
4. [详细实施方案](#详细实施方案)
5. [文件结构规划](#文件结构规划)
6. [实施步骤](#实施步骤)
7. [风险评估](#风险评估)

---

## 需求分析

### 核心需求

1. **新增 UBD Agent 群组**
   - 在 Jaaz 后端新增 3 个 UBD 课程设计 Agent
   - Agent 1: 项目基础定义 (Project Foundation)
   - Agent 2: 评估框架设计 (Assessment Framework)
   - Agent 3: 学习蓝图生成 (Learning Blueprint)

2. **保留原有功能**
   - Jaaz 原有的 Planner 和 ImageVideoCreator Agent 保持不变
   - 图像/视频生成功能正常运行
   - 用户可以选择使用"设计模式"或"课程模式"

3. **用户场景分流**
   - 用户输入"生成图片/视频" → 走原有 Planner Agent 流程
   - 用户输入"创建 PBL 课程" → 走新增 UBD Agent 流程

4. **前端画布增强**
   - 支持显示文本内容节点（课程方案的各个阶段）
   - 文本节点可编辑、可折叠
   - 支持导出完整课程方案为 Markdown 文档

---

## 现状分析

### Jaaz 现有架构

#### 后端 Agent 系统

**文件**: `jaaz/server/services/langgraph_service/agent_manager.py`

**当前 Agent**:
- `planner`: 规划智能体，负责任务分解
- `image_video_creator`: 执行智能体，负责调用图像/视频生成工具

**Agent 创建流程**:
```python
def create_agents(model, tool_list, system_prompt):
    # 过滤工具
    image_tools = [tool for tool in tool_list if tool.get('type') == 'image']
    video_tools = [tool for tool in tool_list if tool.get('type') == 'video']

    # 创建 Agent
    planner_agent = create_langgraph_agent(model, PlannerAgentConfig())
    creator_agent = create_langgraph_agent(model, ImageVideoCreatorAgentConfig(tool_list))

    return [planner_agent, creator_agent]
```

**关键特性**:
- ✅ 支持动态工具注入
- ✅ 支持 Agent 间切换 (Handoff)
- ✅ 支持流式响应
- ⚠️ 硬编码了 Agent 列表（需要改为可配置）

---

#### 前端画布系统

**文件**: `jaaz/react/src/components/canvas/CanvasExcali.tsx`

**当前画布组件**: Excalidraw

**支持的元素类型**:
- `image`: 图像元素
- `embeddable`: 嵌入式视频元素
- `geo`: 几何图形（矩形、圆形等）
- `arrow`: 箭头连接线
- `text`: 文本（但仅作为标注，无结构化内容）

**画布事件监听**:
```typescript
eventBus.on('add-canvas-element', (data) => {
  if (data.type === 'image') {
    // 添加图像到画布
    const imageElement = convertToExcalidrawElements([{
      type: 'image',
      x: data.x,
      y: data.y,
      fileId: data.file_id
    }])
    excalidrawAPI.updateScene({ elements: [...imageElement] })
  }
})
```

**限制**:
- ⚠️ Excalidraw 的 `text` 元素不支持富文本
- ⚠️ 没有专门的"文档节点"概念
- ⚠️ 无导出 Markdown 功能

---

### 痛点识别

#### 1. Agent 创建硬编码
```python
# 当前代码（硬编码）
return [planner_agent, image_video_creator_agent]
```
**问题**: 无法根据用户意图动态选择 Agent 群组

**需要改为**:
```python
def create_agents(model, tool_list, mode='design'):
    if mode == 'design':
        return [planner_agent, image_video_creator_agent]
    elif mode == 'course':
        return [ubd_planner_agent, assessment_agent, blueprint_agent]
```

---

#### 2. 前端缺少文档节点
Excalidraw 的 `text` 元素太简单，无法承载结构化课程内容

**需要新增**:
- 自定义文档卡片组件
- 支持 Markdown 渲染
- 支持折叠/展开
- 支持编辑

---

#### 3. 缺少导出功能
**需要新增**:
- 从画布收集所有文档节点
- 按逻辑顺序组织内容
- 生成 Markdown 文件
- 提供下载接口

---

## 改造架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户输入层                               │
│  "生成图片" → 设计模式    |    "创建 PBL 课程" → 课程模式      │
└────────────┬─────────────────────────────┬──────────────────┘
             │                             │
             ▼                             ▼
┌────────────────────────┐    ┌───────────────────────────────┐
│   原有 Agent 流程       │    │   新增 UBD Agent 流程          │
│  ┌──────────────────┐  │    │  ┌──────────────────────────┐ │
│  │ Planner          │  │    │  │ UBD Planner              │ │
│  │ (任务规划)       │  │    │  │ (理解课程需求)           │ │
│  └────────┬─────────┘  │    │  └────────┬─────────────────┘ │
│           │             │    │           │                   │
│           ▼             │    │           ▼                   │
│  ┌──────────────────┐  │    │  ┌──────────────────────────┐ │
│  │ ImageVideoCreator│  │    │  │ ProjectFoundation        │ │
│  │ (生成图像/视频)  │  │    │  │ (定义项目基础)           │ │
│  └──────────────────┘  │    │  └────────┬─────────────────┘ │
│                         │    │           │                   │
│                         │    │           ▼                   │
│                         │    │  ┌──────────────────────────┐ │
│                         │    │  │ AssessmentDesigner       │ │
│                         │    │  │ (设计评估框架)           │ │
│                         │    │  └────────┬─────────────────┘ │
│                         │    │           │                   │
│                         │    │           ▼                   │
│                         │    │  ┌──────────────────────────┐ │
│                         │    │  │ BlueprintGenerator       │ │
│                         │    │  │ (生成学习蓝图)           │ │
│                         │    │  └──────────────────────────┘ │
└────────────────────────┘    └───────────────────────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      前端画布层                               │
│  ┌───────────────┐       ┌────────────────────────────┐     │
│  │ 图像/视频节点  │       │ 文档卡片节点                │     │
│  │ (Excalidraw)  │       │ (自定义 React 组件)         │     │
│  └───────────────┘       │ - Markdown 渲染             │     │
│                          │ - 可折叠/展开               │     │
│                          │ - 可编辑                    │     │
│                          └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
             │                             │
             └──────────────┬──────────────┘
                            ▼
                   ┌──────────────────┐
                   │  导出 Markdown   │
                   │  文档服务        │
                   └──────────────────┘
```

---

### 核心设计决策

#### Decision 1: 模式切换策略 ✅ 已确定

**✅ 采用方案 A: 用户手动选择模式**

```typescript
// 前端：用户在首页选择
<ModeSelector>
  <Button onClick={() => setMode('design')}>
    🎨 设计模式（图像/视频生成）
  </Button>
  <Button onClick={() => setMode('course')}>
    📚 课程模式（PBL 课程设计）
  </Button>
</ModeSelector>
```

**优点**:
- ✅ 用户意图明确，准确性 100%
- ✅ 逻辑简单，不会误判
- ✅ 易于扩展（未来可以加更多模式）
- ✅ 代码简单，易于维护

**实施细节**:
1. 用户在首页看到两个大卡片，点击选择模式
2. 选择后进入对应的对话界面
3. `mode` 参数随请求传递到后端
4. 后端 AgentManager 根据 `mode` 创建对应的 Agent 群组
5. 整个会话期间模式保持不变
6. 用户可以在首页切换模式（创建新画布）

**废弃方案 B: 自动识别模式**（不采用）

理由：
- ❌ 可能误判（例如"为课程设计一张海报"）
- ❌ 需要维护关键词列表
- ❌ 增加系统复杂度

**决策依据**: Linus 法则 - "简单优于复杂，明确优于猜测"

---

#### Decision 2: Agent 管理器改造

**原有设计（硬编码）**:
```python
class AgentManager:
    @staticmethod
    def create_agents(model, tool_list):
        return [planner_agent, image_video_creator_agent]
```

**新设计（可配置）**:
```python
class AgentManager:
    @staticmethod
    def create_agents(model, tool_list, mode='design'):
        if mode == 'design':
            return AgentManager._create_design_agents(model, tool_list)
        elif mode == 'course':
            return AgentManager._create_course_agents(model, tool_list)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    @staticmethod
    def _create_design_agents(model, tool_list):
        """原有设计模式 Agent"""
        planner_config = PlannerAgentConfig()
        creator_config = ImageVideoCreatorAgentConfig(tool_list)

        planner_agent = AgentManager._create_langgraph_agent(model, planner_config)
        creator_agent = AgentManager._create_langgraph_agent(model, creator_config)

        return [planner_agent, creator_agent]

    @staticmethod
    def _create_course_agents(model, tool_list):
        """新增课程模式 Agent"""
        ubd_planner_config = UBDPlannerAgentConfig()
        foundation_config = ProjectFoundationAgentConfig()
        assessment_config = AssessmentDesignerAgentConfig()
        blueprint_config = BlueprintGeneratorAgentConfig()

        ubd_planner_agent = AgentManager._create_langgraph_agent(model, ubd_planner_config)
        foundation_agent = AgentManager._create_langgraph_agent(model, foundation_config)
        assessment_agent = AgentManager._create_langgraph_agent(model, assessment_config)
        blueprint_agent = AgentManager._create_langgraph_agent(model, blueprint_config)

        return [ubd_planner_agent, foundation_agent, assessment_agent, blueprint_agent]
```

**优点**:
- ✅ 清晰分离两种模式
- ✅ 易于扩展新模式
- ✅ 原有代码几乎不需改动

---

#### Decision 3: 前端文档节点实现

**Excalidraw 的局限性**:
- Excalidraw 主要用于绘图，文本元素功能有限
- 不支持富文本、Markdown 渲染
- 不支持折叠/展开

**解决方案：混合渲染**

```typescript
// 1. 在 Excalidraw 画布上添加占位符矩形
const placeholderRect = {
  type: 'geo',
  id: 'doc-placeholder-1',
  x: 100,
  y: 100,
  props: {
    w: 400,
    h: 300,
    text: '[文档节点]',
    fill: 'pattern'
  }
}

// 2. 在矩形上方覆盖自定义 React 组件
<DocumentCardOverlay
  position={{ x: 100, y: 100 }}
  width={400}
  height={300}
  content={documentContent}
  onEdit={handleEdit}
  onCollapse={handleCollapse}
/>
```

**自定义文档卡片组件**:
```tsx
const DocumentCard = ({ content, position, onEdit }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div
      className="document-card"
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        width: '400px',
        maxHeight: isCollapsed ? '80px' : '500px',
        background: 'white',
        border: '2px solid #4A90E2',
        borderRadius: '8px',
        padding: '16px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        overflow: 'auto'
      }}
    >
      <div className="card-header">
        <h3>{content.title}</h3>
        <button onClick={() => setIsCollapsed(!isCollapsed)}>
          {isCollapsed ? '展开' : '折叠'}
        </button>
        <button onClick={() => setIsEditing(!isEditing)}>
          {isEditing ? '保存' : '编辑'}
        </button>
      </div>

      {!isCollapsed && (
        <div className="card-body">
          {isEditing ? (
            <textarea
              value={content.markdown}
              onChange={(e) => onEdit(e.target.value)}
              style={{ width: '100%', height: '300px' }}
            />
          ) : (
            <ReactMarkdown>{content.markdown}</ReactMarkdown>
          )}
        </div>
      )}
    </div>
  )
}
```

---

#### Decision 4: Markdown 导出策略

**流程**:
```
1. 用户点击"导出课程方案"按钮
   ↓
2. 前端收集所有文档节点数据
   const documents = [
     { stage: 'foundation', title: '项目基础', content: '...' },
     { stage: 'assessment', title: '评估框架', content: '...' },
     { stage: 'blueprint', title: '学习蓝图', content: '...' }
   ]
   ↓
3. 发送到后端 /api/export/markdown
   ↓
4. 后端按模板组织内容
   template = """
   # PBL 课程设计方案

   ## 1. 项目基础定义
   {foundation_content}

   ## 2. 评估框架设计
   {assessment_content}

   ## 3. 学习蓝图
   {blueprint_content}

   ---
   生成时间: {timestamp}
   """
   ↓
5. 返回 Markdown 文件下载链接
   ↓
6. 前端触发下载
```

**后端实现**:
```python
@router.post("/api/export/markdown")
async def export_markdown(data: Dict[str, Any]):
    documents = data.get('documents', [])
    canvas_id = data.get('canvas_id')

    # 组织内容
    markdown_content = generate_course_markdown(documents)

    # 保存文件
    file_path = f"exports/{canvas_id}_{timestamp()}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    # 返回下载链接
    return {
        "download_url": f"/api/file/{file_path}",
        "filename": f"PBL课程方案_{timestamp()}.md"
    }
```

---

## 详细实施方案

### 1. 后端改造

#### 1.1 新增 UBD Agent 配置文件

**目录结构**:
```
jaaz/server/services/langgraph_service/configs/
├── base_config.py                    # ✅ 保持不变
├── planner_config.py                 # ✅ 保持不变
├── image_vide_creator_config.py      # ✅ 保持不变
├── ubd_planner_config.py             # 🆕 新增
├── project_foundation_config.py      # 🆕 新增
├── assessment_designer_config.py     # 🆕 新增
└── blueprint_generator_config.py     # 🆕 新增
```

---

**文件 1: `ubd_planner_config.py`**

```python
from typing import List
from .base_config import BaseAgentConfig, HandoffConfig

class UBDPlannerAgentConfig(BaseAgentConfig):
    """
    UBD 规划智能体

    职责:
    1. 理解用户的课程设计需求
    2. 识别课程主题、学段、学科
    3. 决定是否需要进入 UBD 课程设计流程
    4. 移交给 ProjectFoundation Agent
    """
    def __init__(self) -> None:
        system_prompt = """
你是 UBD（逆向设计）课程规划专家。

你的任务:
1. 分析用户的课程设计需求
2. 识别关键信息:
   - 课程主题
   - 目标学段（小学/初中/高中）
   - 学科领域
   - 学生人数和特点
   - 时间约束

3. 确认是否进入 UBD 课程设计流程

4. 如果确认，立即移交给 project_foundation 智能体

示例对话:
用户: "为高中生设计一个关于环境保护的 PBL 项目"
你: "我理解您想为高中生设计环境保护主题的 PBL 项目。让我为您启动 UBD 课程设计流程..."
[调用 transfer_to_project_foundation 工具]

重要规则:
- 不要自己生成课程内容，只负责理解需求和移交
- 用与用户相同的语言交流
"""

        handoffs: List[HandoffConfig] = [{
            'agent_name': 'project_foundation',
            'description': '移交给项目基础定义智能体，开始 UBD 课程设计'
        }]

        super().__init__(
            name='ubd_planner',
            tools=[],  # 不需要特殊工具
            system_prompt=system_prompt,
            handoffs=handoffs
        )
```

---

**文件 2: `project_foundation_config.py`**

```python
from typing import List
from .base_config import BaseAgentConfig, HandoffConfig

class ProjectFoundationAgentConfig(BaseAgentConfig):
    """
    项目基础定义智能体

    职责:
    1. 定义项目主题和核心驱动问题
    2. 设定学习目标（知识、技能、态度）
    3. 识别核心概念和持久理解
    4. 移交给 Assessment Designer
    """
    def __init__(self) -> None:
        system_prompt = """
你是 UBD 项目基础定义专家，精通确定期望结果（Identify Desired Results）。

你的任务:
1. 定义项目主题
   - 项目名称（吸引人、与主题相关）
   - 项目概述（200字左右）

2. 提炼核心驱动问题（Essential Question）
   - 开放性、能激发深度思考
   - 与真实世界相关
   - 没有唯一答案

3. 设定学习目标
   - 知识目标：学生将知道什么？
   - 技能目标：学生将能够做什么？
   - 态度目标：学生将形成什么价值观？

4. 识别核心概念和持久理解（Enduring Understanding）
   - 超越事实的深层理解
   - 可迁移到其他情境

5. 调用 define_project_foundation 工具保存结果

6. 完成后，移交给 assessment_designer 智能体

输出示例（环保主题）:
```markdown
## 项目基础定义

**项目名称**: 绿色家园守护者

**项目概述**:
学生将化身环保行动者，调查社区的环境问题，设计并实施改善方案。
通过真实的社区调研、数据分析、方案设计，学生将理解人类活动对环境的影响，
培养环保意识和公民责任感。

**核心驱动问题**:
"我们如何成为社区环境的守护者？"

**学习目标**:
- 知识：理解生态系统、环境污染、可持续发展等概念
- 技能：调研能力、数据分析、方案设计、团队协作
- 态度：环保意识、社会责任感、批判性思维

**持久理解**:
- 人类活动与环境健康密切相关
- 每个人都可以为环境保护做出贡献
- 可持续发展需要平衡经济、社会、环境三方面
```

重要规则:
- 使用 UBD 框架的专业术语
- 核心驱动问题要高质量（开放、有深度）
- 学习目标要具体、可测量
- 完成后必须调用工具保存，然后移交
"""

        handoffs: List[HandoffConfig] = [{
            'agent_name': 'assessment_designer',
            'description': '移交给评估框架设计智能体'
        }]

        super().__init__(
            name='project_foundation',
            tools=[{'id': 'define_project_foundation', 'provider': 'system'}],
            system_prompt=system_prompt,
            handoffs=handoffs
        )
```

---

**文件 3: `assessment_designer_config.py`**

```python
from typing import List
from .base_config import BaseAgentConfig, HandoffConfig

class AssessmentDesignerAgentConfig(BaseAgentConfig):
    """
    评估框架设计智能体

    职责:
    1. 基于学习目标设计评估标准
    2. 创建评估量规（Rubric）
    3. 规划评估时间点（形成性 + 总结性）
    4. 移交给 Blueprint Generator
    """
    def __init__(self) -> None:
        system_prompt = """
你是 UBD 评估框架设计专家，精通确定合适的评估证据（Determine Acceptable Evidence）。

你的任务:
1. 设计评估标准
   - 基于前一阶段定义的学习目标
   - 包含知识、技能、态度三个维度
   - 每个标准要具体、可观察、可测量

2. 创建评估量规（Rubric）
   - 4 个等级：优秀、良好、及格、需改进
   - 每个标准在每个等级的具体描述
   - 表格形式呈现

3. 规划评估时间点
   - 形成性评估：项目进行中的检查点
   - 总结性评估：项目结束时的最终成果
   - 每个评估点的评估方式和重点

4. 调用 design_assessment_framework 工具保存结果

5. 完成后，移交给 blueprint_generator 智能体

输出示例:
```markdown
## 评估框架设计

### 评估标准

| 维度 | 评估标准 |
|------|---------|
| 知识 | 能够解释环境问题的成因和影响 |
| 技能 | 能够使用科学方法调研和分析数据 |
| 态度 | 展现出对环保行动的主动性和责任感 |

### 评估量规

#### 标准 1: 环境问题理解

| 等级 | 描述 |
|------|------|
| 优秀 (4) | 深入理解环境问题的复杂成因，能够分析多方面的影响，并提出系统性见解 |
| 良好 (3) | 能够解释环境问题的主要成因和影响，理解基本的因果关系 |
| 及格 (2) | 能够识别环境问题，但对成因和影响的理解较为表面 |
| 需改进 (1) | 对环境问题的理解不清晰或存在明显误解 |

#### 标准 2: 调研与分析能力
[类似表格...]

### 评估时间线

| 时间点 | 评估类型 | 评估方式 | 评估重点 |
|--------|---------|---------|---------|
| 第 1 周末 | 形成性 | 小组讨论 + 教师观察 | 问题识别和调研计划 |
| 第 3 周末 | 形成性 | 数据分析报告 | 数据收集和分析能力 |
| 第 5 周末 | 总结性 | 最终成果展示 + 反思报告 | 综合评估所有目标 |
```

重要规则:
- 评估标准必须与学习目标一一对应
- 量规描述要具体，避免模糊词汇
- 形成性评估要及时、频繁，帮助学生改进
- 完成后必须调用工具保存，然后移交
"""

        handoffs: List[HandoffConfig] = [{
            'agent_name': 'blueprint_generator',
            'description': '移交给学习蓝图生成智能体'
        }]

        super().__init__(
            name='assessment_designer',
            tools=[{'id': 'design_assessment_framework', 'provider': 'system'}],
            system_prompt=system_prompt,
            handoffs=handoffs
        )
```

---

**文件 4: `blueprint_generator_config.py`**

```python
from typing import List
from .base_config import BaseAgentConfig, HandoffConfig

class BlueprintGeneratorAgentConfig(BaseAgentConfig):
    """
    学习蓝图生成智能体

    职责:
    1. 设计学习活动序列
    2. 为每个活动分配时间、资源、评估节点
    3. 生成完整的学习蓝图
    4. 可选：导出 Markdown 文档
    """
    def __init__(self) -> None:
        system_prompt = """
你是 UBD 学习蓝图设计专家，精通规划学习体验和教学（Plan Learning Experiences and Instruction）。

你的任务:
1. 设计学习活动序列
   - 基于前面定义的目标和评估
   - 遵循 "钩子 → 探索 → 解释 → 拓展 → 评价" (5E) 模式
   - 每个活动包含：名称、时长、目标、流程、资源

2. 活动详细规划
   - 活动目标：该活动要达成什么？
   - 活动流程：学生做什么？教师做什么？
   - 所需资源：材料、工具、场地等
   - 评估节点：在哪里嵌入评估？

3. 时间安排
   - 整体项目时长（例如 6 周）
   - 每周的重点活动
   - 关键里程碑

4. 资源清单
   - 教学资源（视频、文章、案例等）
   - 工具和设备
   - 外部支持（专家、社区资源等）

5. 调用 generate_learning_blueprint 工具保存结果

6. （可选）调用 export_markdown 工具生成完整文档

输出示例:
```markdown
## 学习蓝图

### 项目时长
6 周（每周 3 课时，共 18 课时）

### 学习活动序列

#### 第 1-2 周：钩子与探索（Engage & Explore）

**活动 1: 环保问题发现之旅**
- 目标：激发兴趣，识别社区环境问题
- 时长：2 课时
- 流程：
  1. 观看环境纪录片片段（15 分钟）
  2. 小组讨论：我们社区存在哪些环境问题？（20 分钟）
  3. 实地考察：学校周边环境调研（40 分钟）
  4. 记录观察结果和初步想法（10 分钟）
- 资源：纪录片、调研表格、相机
- 评估：观察学生参与度和问题识别能力

**活动 2: 问题聚焦工作坊**
- 目标：选定一个重点问题进行深入研究
- 时长：2 课时
- 流程：
  1. 小组分享调研发现（30 分钟）
  2. 投票选择最关心的问题（15 分钟）
  3. 制定调研计划（30 分钟）
  4. 确定数据收集方法（10 分钟）
- 资源：投票工具、计划模板
- 评估：调研计划的完整性和可行性

[继续其他活动...]

#### 第 3-4 周：解释与深化（Explain & Elaborate）

**活动 3: 数据收集与分析**
[详细内容...]

**活动 4: 专家访谈**
[详细内容...]

#### 第 5-6 周：拓展与评价（Extend & Evaluate）

**活动 5: 方案设计**
[详细内容...]

**活动 6: 成果展示与反思**
[详细内容...]

### 资源清单

**教学资源**:
- 《寂静的春天》选段
- 环保纪录片《地球脉动》
- 数据分析工具：Excel/Google Sheets

**工具和设备**:
- 空气质量检测仪
- 水质检测试剂盒
- 相机/手机

**外部支持**:
- 环保局专家讲座
- 社区环保组织合作
```

重要规则:
- 活动要循序渐进，从简单到复杂
- 确保活动与评估标准对齐
- 提供足够的脚手架（Scaffolding）支持学生
- 预留学生反思和调整的时间
- 完成后必须调用工具保存
"""

        handoffs: List[HandoffConfig] = []  # 最后一个 Agent，不需要移交

        super().__init__(
            name='blueprint_generator',
            tools=[
                {'id': 'generate_learning_blueprint', 'provider': 'system'},
                {'id': 'export_course_markdown', 'provider': 'system'}
            ],
            system_prompt=system_prompt,
            handoffs=handoffs
        )
```

---

#### 1.2 修改 AgentManager

**文件**: `jaaz/server/services/langgraph_service/agent_manager.py`

```python
from typing import List, Dict, Any, Optional
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph
from langchain_core.tools import BaseTool
from models.tool_model import ToolInfoJson

# 导入原有配置
from .configs import (
    PlannerAgentConfig,
    ImageVideoCreatorAgentConfig,
    create_handoff_tool,
    BaseAgentConfig
)

# 导入新增配置
from .configs.ubd_planner_config import UBDPlannerAgentConfig
from .configs.project_foundation_config import ProjectFoundationAgentConfig
from .configs.assessment_designer_config import AssessmentDesignerAgentConfig
from .configs.blueprint_generator_config import BlueprintGeneratorAgentConfig

from services.tool_service import tool_service


class AgentManager:
    """智能体管理器 - 负责创建和管理所有智能体"""

    @staticmethod
    def create_agents(
        model: Any,
        tool_list: List[ToolInfoJson],
        mode: str = "design",  # 🆕 新增 mode 参数
        system_prompt: str = ""
    ) -> List[CompiledGraph]:
        """
        创建智能体群组

        Args:
            model: 语言模型实例
            tool_list: 工具列表
            mode: 模式选择 ('design' 或 'course')
            system_prompt: 系统提示词

        Returns:
            智能体列表
        """
        if mode == "design":
            return AgentManager._create_design_agents(model, tool_list, system_prompt)
        elif mode == "course":
            return AgentManager._create_course_agents(model, tool_list, system_prompt)
        else:
            raise ValueError(f"Unknown mode: {mode}. Must be 'design' or 'course'.")

    @staticmethod
    def _create_design_agents(
        model: Any,
        tool_list: List[ToolInfoJson],
        system_prompt: str = ""
    ) -> List[CompiledGraph]:
        """
        创建设计模式 Agent（原有功能）

        返回:
        - Planner Agent
        - ImageVideoCreator Agent
        """
        # 过滤工具
        image_tools = [tool for tool in tool_list if tool.get('type') == 'image']
        video_tools = [tool for tool in tool_list if tool.get('type') == 'video']

        print(f"📸 图像工具: {image_tools}")
        print(f"🎬 视频工具: {video_tools}")

        # 创建 Agent
        planner_config = PlannerAgentConfig()
        planner_agent = AgentManager._create_langgraph_agent(model, planner_config)

        creator_config = ImageVideoCreatorAgentConfig(tool_list)
        creator_agent = AgentManager._create_langgraph_agent(model, creator_config)

        return [planner_agent, creator_agent]

    @staticmethod
    def _create_course_agents(
        model: Any,
        tool_list: List[ToolInfoJson],
        system_prompt: str = ""
    ) -> List[CompiledGraph]:
        """
        创建课程模式 Agent（新增功能）

        返回:
        - UBD Planner Agent
        - ProjectFoundation Agent
        - AssessmentDesigner Agent
        - BlueprintGenerator Agent
        """
        print(f"📚 创建 UBD 课程设计 Agent 群组")

        # 创建 Agent
        ubd_planner_config = UBDPlannerAgentConfig()
        ubd_planner_agent = AgentManager._create_langgraph_agent(model, ubd_planner_config)

        foundation_config = ProjectFoundationAgentConfig()
        foundation_agent = AgentManager._create_langgraph_agent(model, foundation_config)

        assessment_config = AssessmentDesignerAgentConfig()
        assessment_agent = AgentManager._create_langgraph_agent(model, assessment_config)

        blueprint_config = BlueprintGeneratorAgentConfig()
        blueprint_agent = AgentManager._create_langgraph_agent(model, blueprint_config)

        return [ubd_planner_agent, foundation_agent, assessment_agent, blueprint_agent]

    @staticmethod
    def _create_langgraph_agent(
        model: Any,
        config: BaseAgentConfig
    ) -> CompiledGraph:
        """
        根据配置创建单个 LangGraph 智能体

        （保持不变）
        """
        # 创建 Handoff 工具
        handoff_tools: List[BaseTool] = []
        for handoff in config.handoffs:
            handoff_tool = create_handoff_tool(
                agent_name=handoff['agent_name'],
                description=handoff['description'],
            )
            if handoff_tool:
                handoff_tools.append(handoff_tool)

        # 获取业务工具
        business_tools: List[BaseTool] = []
        for tool_json in config.tools:
            tool = tool_service.get_tool(tool_json['id'])
            if tool:
                business_tools.append(tool)

        # 创建 LangGraph Agent
        return create_react_agent(
            name=config.name,
            model=model,
            tools=[*business_tools, *handoff_tools],
            prompt=config.system_prompt
        )

    @staticmethod
    def get_last_active_agent(
        messages: List[Dict[str, Any]],
        agent_names: List[str]
    ) -> Optional[str]:
        """
        获取最后活跃的智能体

        （保持不变）
        """
        for message in reversed(messages):
            if message.get('role') == 'assistant':
                message_name = message.get('name')
                if message_name and message_name in agent_names:
                    return message_name
        return None
```

---

#### 1.3 修改 agent_service.py

**文件**: `jaaz/server/services/langgraph_service/agent_service.py`

```python
# 在 langgraph_multi_agent 函数中新增 mode 参数

async def langgraph_multi_agent(
    messages: List[Dict[str, Any]],
    canvas_id: str,
    session_id: str,
    text_model: ModelInfo,
    tool_list: List[ToolInfoJson],
    mode: str = "design",  # 🆕 新增参数
    system_prompt: Optional[str] = None
) -> None:
    """
    多智能体处理函数

    Args:
        messages: 消息历史
        canvas_id: 画布ID
        session_id: 会话ID
        text_model: 文本模型配置
        tool_list: 工具模型配置列表
        mode: 模式 ('design' 或 'course')  # 🆕
        system_prompt: 系统提示词
    """
    try:
        # 0. 修复消息历史
        fixed_messages = _fix_chat_history(messages)

        # 1. 创建文本模型
        text_model_instance = _create_text_model(text_model)

        # 2. 创建智能体（🆕 传入 mode 参数）
        agents = AgentManager.create_agents(
            text_model_instance,
            tool_list,
            mode=mode,  # 🆕
            system_prompt=system_prompt or ""
        )
        agent_names = [agent.name for agent in agents]
        print('👇 agent_names', agent_names)

        last_agent = AgentManager.get_last_active_agent(fixed_messages, agent_names)
        print('👇 last_agent', last_agent)

        # 3. 创建 Swarm
        swarm = create_swarm(
            agents=agents,
            default_active_agent=last_agent if last_agent else agent_names[0]
        )

        # 4. 创建上下文（🆕 包含 mode）
        context = {
            'canvas_id': canvas_id,
            'session_id': session_id,
            'tool_list': tool_list,
            'mode': mode  # 🆕
        }

        # 5. 流式处理
        processor = StreamProcessor(session_id, db_service, send_to_websocket)
        await processor.process_stream(swarm, fixed_messages, context)

    except Exception as e:
        await _handle_error(e, session_id)
```

---

#### 1.4 修改 chat_service.py

**文件**: `jaaz/server/services/chat_service.py`

```python
async def handle_chat(data: Dict[str, Any]) -> None:
    """
    Handle an incoming chat request.

    🆕 新增 mode 参数处理
    """
    messages: List[Dict[str, Any]] = data.get('messages', [])
    session_id: str = data.get('session_id', '')
    canvas_id: str = data.get('canvas_id', '')
    text_model: ModelInfo = data.get('text_model', {})
    tool_list: List[ToolInfoJson] = data.get('tool_list', [])
    mode: str = data.get('mode', 'design')  # 🆕 默认为 design 模式
    system_prompt: Optional[str] = data.get('system_prompt')

    print(f'👇 chat_service mode: {mode}')  # 🆕
    print('👇 chat_service got tool_list', tool_list)

    # 创建会话
    if len(messages) == 1:
        await db_service.create_chat_session(
            session_id,
            text_model.get('model'),
            text_model.get('provider'),
            canvas_id,
            (messages[0].get('content')[:200] if isinstance(messages[0].get('content'), str) else '')
        )

    # 保存消息
    await db_service.create_message(
        session_id,
        messages[-1].get('role', 'user'),
        json.dumps(messages[-1])
    ) if len(messages) > 0 else None

    # 创建 Agent 任务（🆕 传入 mode）
    task = asyncio.create_task(langgraph_multi_agent(
        messages,
        canvas_id,
        session_id,
        text_model,
        tool_list,
        mode=mode,  # 🆕
        system_prompt=system_prompt
    ))

    add_stream_task(session_id, task)
    try:
        await task
    except asyncio.exceptions.CancelledError:
        print(f"🛑 Session {session_id} cancelled during stream")
    finally:
        remove_stream_task(session_id)
        await send_to_websocket(session_id, {'type': 'done'})
```

---

#### 1.5 新增 UBD 工具函数

**目录结构**:
```
jaaz/server/tools/
├── ubd_tools.py              # 🆕 新增
└── export_tools.py           # 🆕 新增
```

**文件 1: `tools/ubd_tools.py`**

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json

from services.websocket_service import send_to_websocket
from services.tool_service import tool_service


# ========== 工具 1: 定义项目基础 ==========

class ProjectFoundationInput(BaseModel):
    """项目基础定义输入"""
    project_name: str = Field(description="项目名称")
    project_overview: str = Field(description="项目概述")
    essential_question: str = Field(description="核心驱动问题")
    learning_objectives: Dict[str, List[str]] = Field(
        description="学习目标，格式: {'knowledge': [...], 'skills': [...], 'attitudes': [...]}"
    )
    enduring_understandings: List[str] = Field(description="持久理解列表")


async def define_project_foundation(
    project_name: str,
    project_overview: str,
    essential_question: str,
    learning_objectives: Dict[str, List[str]],
    enduring_understandings: List[str],
    **kwargs
) -> str:
    """
    定义项目基础

    保存项目基础信息并推送到画布
    """
    canvas_id = kwargs.get('canvas_id')
    session_id = kwargs.get('session_id')

    # 组织数据
    foundation_data = {
        'stage': 'foundation',
        'project_name': project_name,
        'project_overview': project_overview,
        'essential_question': essential_question,
        'learning_objectives': learning_objectives,
        'enduring_understandings': enduring_understandings
    }

    # 生成 Markdown 内容
    markdown_content = f"""## 项目基础定义

**项目名称**: {project_name}

**项目概述**:
{project_overview}

**核心驱动问题**:
"{essential_question}"

**学习目标**:
- **知识目标**:
{''.join([f'  - {obj}\n' for obj in learning_objectives.get('knowledge', [])])}
- **技能目标**:
{''.join([f'  - {obj}\n' for obj in learning_objectives.get('skills', [])])}
- **态度目标**:
{''.join([f'  - {obj}\n' for obj in learning_objectives.get('attitudes', [])])}

**持久理解**:
{''.join([f'- {understanding}\n' for understanding in enduring_understandings])}
"""

    foundation_data['markdown'] = markdown_content

    # 推送到前端画布
    await send_to_websocket(session_id, {
        'type': 'add_document_card',
        'data': foundation_data
    })

    print(f"✅ 项目基础定义完成: {project_name}")

    return f"项目基础定义已完成并添加到画布。项目名称: {project_name}"


# 注册工具
define_project_foundation_tool = StructuredTool.from_function(
    func=define_project_foundation,
    name='define_project_foundation',
    description='定义 PBL 项目的基础信息，包括项目名称、核心问题、学习目标等',
    args_schema=ProjectFoundationInput,
    coroutine=define_project_foundation
)

tool_service.register_tool('define_project_foundation', define_project_foundation_tool)


# ========== 工具 2: 设计评估框架 ==========

class AssessmentFrameworkInput(BaseModel):
    """评估框架输入"""
    assessment_criteria: List[Dict[str, str]] = Field(
        description="评估标准列表，格式: [{'dimension': '知识', 'criterion': '...'}]"
    )
    rubric: Dict[str, Dict[str, str]] = Field(
        description="评估量规，格式: {'标准1': {'优秀': '...', '良好': '...', '及格': '...', '需改进': '...'}}"
    )
    assessment_timeline: List[Dict[str, str]] = Field(
        description="评估时间线，格式: [{'time': '第1周', 'type': '形成性', 'method': '...', 'focus': '...'}]"
    )


async def design_assessment_framework(
    assessment_criteria: List[Dict[str, str]],
    rubric: Dict[str, Dict[str, str]],
    assessment_timeline: List[Dict[str, str]],
    **kwargs
) -> str:
    """
    设计评估框架

    保存评估标准、量规和时间线，并推送到画布
    """
    session_id = kwargs.get('session_id')

    # 组织数据
    assessment_data = {
        'stage': 'assessment',
        'assessment_criteria': assessment_criteria,
        'rubric': rubric,
        'assessment_timeline': assessment_timeline
    }

    # 生成 Markdown 内容
    criteria_table = "| 维度 | 评估标准 |\n|------|----------|\n"
    criteria_table += "\n".join([
        f"| {item['dimension']} | {item['criterion']} |"
        for item in assessment_criteria
    ])

    rubric_sections = []
    for criterion_name, levels in rubric.items():
        rubric_section = f"#### {criterion_name}\n\n| 等级 | 描述 |\n|------|------|\n"
        level_order = ['优秀', '良好', '及格', '需改进']
        for level in level_order:
            if level in levels:
                rubric_section += f"| {level} | {levels[level]} |\n"
        rubric_sections.append(rubric_section)

    timeline_table = "| 时间点 | 评估类型 | 评估方式 | 评估重点 |\n|--------|----------|----------|----------|\n"
    timeline_table += "\n".join([
        f"| {item['time']} | {item['type']} | {item['method']} | {item['focus']} |"
        for item in assessment_timeline
    ])

    markdown_content = f"""## 评估框架设计

### 评估标准

{criteria_table}

### 评估量规

{chr(10).join(rubric_sections)}

### 评估时间线

{timeline_table}
"""

    assessment_data['markdown'] = markdown_content

    # 推送到前端画布
    await send_to_websocket(session_id, {
        'type': 'add_document_card',
        'data': assessment_data
    })

    print(f"✅ 评估框架设计完成，包含 {len(assessment_criteria)} 个标准")

    return f"评估框架设计已完成并添加到画布。包含 {len(assessment_criteria)} 个评估标准。"


# 注册工具
design_assessment_framework_tool = StructuredTool.from_function(
    func=design_assessment_framework,
    name='design_assessment_framework',
    description='设计 PBL 项目的评估框架，包括评估标准、量规和时间线',
    args_schema=AssessmentFrameworkInput,
    coroutine=design_assessment_framework
)

tool_service.register_tool('design_assessment_framework', design_assessment_framework_tool)


# ========== 工具 3: 生成学习蓝图 ==========

class LearningBlueprintInput(BaseModel):
    """学习蓝图输入"""
    project_duration: str = Field(description="项目总时长，如 '6周'")
    learning_activities: List[Dict[str, Any]] = Field(
        description="学习活动列表，每个活动包含: name, phase, duration, objective, procedure, resources, assessment"
    )
    resource_list: List[Dict[str, str]] = Field(
        description="资源清单，格式: [{'category': '教学资源', 'items': ['...']}]"
    )


async def generate_learning_blueprint(
    project_duration: str,
    learning_activities: List[Dict[str, Any]],
    resource_list: List[Dict[str, str]],
    **kwargs
) -> str:
    """
    生成学习蓝图

    保存学习活动序列和资源清单，并推送到画布
    """
    session_id = kwargs.get('session_id')

    # 组织数据
    blueprint_data = {
        'stage': 'blueprint',
        'project_duration': project_duration,
        'learning_activities': learning_activities,
        'resource_list': resource_list
    }

    # 生成 Markdown 内容
    # 按阶段分组活动
    phases = {}
    for activity in learning_activities:
        phase = activity.get('phase', '其他')
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(activity)

    activities_md = ""
    for phase, activities in phases.items():
        activities_md += f"#### {phase}\n\n"
        for activity in activities:
            activities_md += f"""**{activity['name']}**
- 目标: {activity['objective']}
- 时长: {activity['duration']}
- 流程:
{activity['procedure']}
- 资源: {', '.join(activity['resources'])}
- 评估: {activity['assessment']}

"""

    resources_md = ""
    for category in resource_list:
        resources_md += f"**{category['category']}**:\n"
        resources_md += "\n".join([f"- {item}" for item in category['items']])
        resources_md += "\n\n"

    markdown_content = f"""## 学习蓝图

### 项目时长
{project_duration}

### 学习活动序列

{activities_md}

### 资源清单

{resources_md}
"""

    blueprint_data['markdown'] = markdown_content

    # 推送到前端画布
    await send_to_websocket(session_id, {
        'type': 'add_document_card',
        'data': blueprint_data
    })

    print(f"✅ 学习蓝图生成完成，包含 {len(learning_activities)} 个活动")

    return f"学习蓝图已完成并添加到画布。包含 {len(learning_activities)} 个学习活动。"


# 注册工具
generate_learning_blueprint_tool = StructuredTool.from_function(
    func=generate_learning_blueprint,
    name='generate_learning_blueprint',
    description='生成 PBL 项目的学习蓝图，包括活动序列和资源清单',
    args_schema=LearningBlueprintInput,
    coroutine=generate_learning_blueprint
)

tool_service.register_tool('generate_learning_blueprint', generate_learning_blueprint_tool)
```

---

**文件 2: `tools/export_tools.py`**

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
import os

from services.websocket_service import send_to_websocket
from services.tool_service import tool_service
from services.db_service import db_service


class ExportMarkdownInput(BaseModel):
    """Markdown 导出输入"""
    canvas_id: str = Field(description="画布ID")
    include_metadata: bool = Field(default=True, description="是否包含元数据")


async def export_course_markdown(
    canvas_id: str,
    include_metadata: bool = True,
    **kwargs
) -> str:
    """
    导出课程方案为 Markdown 文档

    从数据库或画布获取所有文档节点，按顺序组织为完整的 Markdown 文件
    """
    session_id = kwargs.get('session_id')

    # 从数据库获取画布相关的所有消息
    # 这里需要解析消息中的文档节点数据
    # 实际实现时，可能需要在数据库中新增专门的文档节点表

    # 模拟获取文档节点（实际应从数据库查询）
    documents = []
    # TODO: 实现从数据库或画布获取文档节点的逻辑

    # 生成 Markdown 内容
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown_content = f"""# PBL 课程设计方案

> **生成时间**: {timestamp}
> **画布ID**: {canvas_id}

---

## 1. 项目基础定义

[项目基础内容]

---

## 2. 评估框架设计

[评估框架内容]

---

## 3. 学习蓝图

[学习蓝图内容]

---

*本课程方案由 Jaaz PBL 课程设计助手自动生成*
"""

    # 保存文件
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    filename = f"PBL_Course_{canvas_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    file_path = os.path.join(export_dir, filename)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    # 推送下载链接到前端
    await send_to_websocket(session_id, {
        'type': 'document_ready',
        'download_url': f'/api/file/{file_path}',
        'filename': filename
    })

    print(f"✅ 课程方案已导出: {filename}")

    return f"课程方案已导出为 Markdown 文档: {filename}"


# 注册工具
export_course_markdown_tool = StructuredTool.from_function(
    func=export_course_markdown,
    name='export_course_markdown',
    description='将完整的 PBL 课程方案导出为 Markdown 文档',
    args_schema=ExportMarkdownInput,
    coroutine=export_course_markdown
)

tool_service.register_tool('export_course_markdown', export_course_markdown_tool)
```

---

### 2. 前端改造

#### 2.1 新增模式选择界面

**文件**: `jaaz/react/src/routes/index.tsx`

```typescript
import { useState } from 'react'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { createCanvas } from '@/api/canvas'
import ChatTextarea from '@/components/chat/ChatTextarea'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { ImageIcon, BookOpen } from 'lucide-react'
import { nanoid } from 'nanoid'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const navigate = useNavigate()
  const [selectedMode, setSelectedMode] = useState<'design' | 'course' | null>(null)

  const handleModeSelect = (mode: 'design' | 'course') => {
    setSelectedMode(mode)
  }

  const handleStartChat = async (messages: any[], configs: any) => {
    if (!selectedMode) {
      alert('请先选择模式')
      return
    }

    const canvasData = {
      name: selectedMode === 'design' ? '设计画布' : 'PBL 课程方案',
      canvas_id: nanoid(),
      messages: messages,
      session_id: nanoid(),
      text_model: configs.textModel,
      tool_list: configs.toolList,
      mode: selectedMode,  // 🆕 传递模式
      system_prompt: localStorage.getItem('system_prompt') || ''
    }

    const result = await createCanvas(canvasData)

    navigate({
      to: '/canvas/$id',
      params: { id: result.id },
      search: {
        sessionId: canvasData.session_id,
        mode: selectedMode  // 🆕 传递到画布页面
      }
    })
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-12">欢迎使用 Jaaz</h1>

      {/* 模式选择 */}
      {!selectedMode && (
        <div className="grid grid-cols-2 gap-6 mb-12">
          <Card
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => handleModeSelect('design')}
          >
            <CardHeader className="text-center">
              <ImageIcon className="w-16 h-16 mx-auto mb-4 text-blue-500" />
              <CardTitle>设计模式</CardTitle>
              <CardDescription>
                生成图像、视频等创意内容
              </CardDescription>
            </CardHeader>
          </Card>

          <Card
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => handleModeSelect('course')}
          >
            <CardHeader className="text-center">
              <BookOpen className="w-16 h-16 mx-auto mb-4 text-green-500" />
              <CardTitle>课程模式</CardTitle>
              <CardDescription>
                设计 PBL 项目式学习课程
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      )}

      {/* 已选择模式 */}
      {selectedMode && (
        <div className="w-full max-w-2xl">
          <div className="flex items-center gap-4 mb-6">
            <span className="text-lg">
              当前模式:
              <strong className="ml-2">
                {selectedMode === 'design' ? '🎨 设计模式' : '📚 课程模式'}
              </strong>
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedMode(null)}
            >
              切换模式
            </Button>
          </div>

          <ChatTextarea
            messages={[]}
            onSendMessages={handleStartChat}
            placeholder={
              selectedMode === 'design'
                ? '描述你想生成的图像或视频...'
                : '描述你想设计的 PBL 课程项目...'
            }
          />
        </div>
      )}
    </div>
  )
}
```

---

#### 2.2 创建文档卡片组件

**文件**: `jaaz/react/src/components/canvas/DocumentCard.tsx`

```typescript
import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ChevronDown, ChevronRight, Edit, Save, Copy } from 'lucide-react'

interface DocumentCardProps {
  id: string
  data: {
    stage: string
    markdown: string
    [key: string]: any
  }
  position: { x: number; y: number }
  onUpdate?: (id: string, newContent: string) => void
}

const DocumentCard: React.FC<DocumentCardProps> = ({
  id,
  data,
  position,
  onUpdate
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState(data.markdown)

  const stageNames = {
    foundation: '📌 项目基础定义',
    assessment: '📊 评估框架设计',
    blueprint: '🗺️ 学习蓝图'
  }

  const stageColors = {
    foundation: 'border-blue-500 bg-blue-50',
    assessment: 'border-orange-500 bg-orange-50',
    blueprint: 'border-green-500 bg-green-50'
  }

  const handleSave = () => {
    if (onUpdate) {
      onUpdate(id, editedContent)
    }
    setIsEditing(false)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(data.markdown)
    // TODO: 显示复制成功提示
  }

  return (
    <div
      className={`document-card ${stageColors[data.stage]} border-2 rounded-lg shadow-lg`}
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        width: '450px',
        maxHeight: isCollapsed ? '80px' : '600px',
        overflow: 'auto',
        zIndex: 1000,
        padding: '16px'
      }}
    >
      {/* 卡片头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="text-gray-600 hover:text-gray-900"
          >
            {isCollapsed ? <ChevronRight /> : <ChevronDown />}
          </button>
          <h3 className="text-lg font-bold">
            {stageNames[data.stage] || data.stage}
          </h3>
        </div>

        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? <Save className="w-4 h-4" /> : <Edit className="w-4 h-4" />}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleCopy}
          >
            <Copy className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* 卡片内容 */}
      {!isCollapsed && (
        <div className="card-body">
          {isEditing ? (
            <Textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full h-[500px] font-mono text-sm"
            />
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{data.markdown}</ReactMarkdown>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DocumentCard
```

---

#### 2.3 修改画布组件，添加文档卡片渲染

**文件**: `jaaz/react/src/components/canvas/CanvasExcali.tsx`

```typescript
import { useState, useEffect, useRef } from 'react'
import { Excalidraw } from '@excalidraw/excalidraw'
import { useCanvas } from '@/contexts/canvas'
import { eventBus } from '@/lib/event'
import DocumentCard from './DocumentCard'

const CanvasExcali = ({ canvasId, initialData }) => {
  const { excalidrawAPI, setExcalidrawAPI } = useCanvas()
  const [documentCards, setDocumentCards] = useState<any[]>([])

  useEffect(() => {
    // 监听添加文档卡片事件
    const handleAddDocumentCard = (data: any) => {
      console.log('📝 添加文档卡片:', data)

      // 计算卡片位置（自动布局）
      const cardIndex = documentCards.length
      const xOffset = 100
      const yOffset = 100 + cardIndex * 650

      const newCard = {
        id: `doc-card-${Date.now()}`,
        data: data,
        position: { x: xOffset, y: yOffset }
      }

      setDocumentCards((prev) => [...prev, newCard])

      // 可选：在 Excalidraw 画布上添加占位符矩形
      if (excalidrawAPI) {
        const placeholderRect = {
          type: 'rectangle',
          x: xOffset,
          y: yOffset,
          width: 450,
          height: 80,
          strokeColor: '#4A90E2',
          backgroundColor: '#E3F2FD',
          fillStyle: 'solid',
          strokeWidth: 2,
          roundness: { type: 3 }
        }

        // excalidrawAPI.addFiles([placeholderRect])
        // 注意：这个 API 需要根据 Excalidraw 的实际版本调整
      }
    }

    eventBus.on('add_document_card', handleAddDocumentCard)

    return () => {
      eventBus.off('add_document_card', handleAddDocumentCard)
    }
  }, [excalidrawAPI, documentCards])

  const handleUpdateDocument = (id: string, newContent: string) => {
    setDocumentCards((prev) =>
      prev.map((card) =>
        card.id === id
          ? { ...card, data: { ...card.data, markdown: newContent } }
          : card
      )
    )
  }

  return (
    <div className="relative w-full h-full">
      {/* Excalidraw 画布 */}
      <Excalidraw
        ref={(api) => setExcalidrawAPI(api)}
        initialData={initialData}
        onChange={(elements, appState, files) => {
          // 自动保存
          // handleSave(elements, appState, files)
        }}
      />

      {/* 文档卡片覆盖层 */}
      {documentCards.map((card) => (
        <DocumentCard
          key={card.id}
          id={card.id}
          data={card.data}
          position={card.position}
          onUpdate={handleUpdateDocument}
        />
      ))}
    </div>
  )
}

export default CanvasExcali
```

---

#### 2.4 添加导出功能

**文件**: `jaaz/react/src/components/canvas/CanvasHeader.tsx`

```typescript
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'
import { useSearch } from '@tanstack/react-router'

const CanvasHeader = ({ canvasId, canvasName }) => {
  const search = useSearch({ from: '/canvas/$id' }) as { mode?: string }
  const mode = search?.mode || 'design'

  const handleExportMarkdown = async () => {
    // 调用导出 API
    const response = await fetch('/api/export/markdown', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ canvas_id: canvasId })
    })

    const result = await response.json()

    // 触发下载
    const link = document.createElement('a')
    link.href = result.download_url
    link.download = result.filename
    link.click()
  }

  return (
    <header className="flex items-center justify-between p-4 border-b">
      <h1 className="text-xl font-bold">{canvasName}</h1>

      <div className="flex gap-2">
        {mode === 'course' && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportMarkdown}
          >
            <Download className="w-4 h-4 mr-2" />
            导出 Markdown
          </Button>
        )}
        {/* 其他按钮 */}
      </div>
    </header>
  )
}

export default CanvasHeader
```

---

## 文件结构规划

### 后端新增文件

```
jaaz/server/
├── services/
│   └── langgraph_service/
│       └── configs/
│           ├── ubd_planner_config.py              # 🆕
│           ├── project_foundation_config.py       # 🆕
│           ├── assessment_designer_config.py      # 🆕
│           └── blueprint_generator_config.py      # 🆕
│
├── tools/
│   ├── ubd_tools.py                               # 🆕
│   └── export_tools.py                            # 🆕
│
└── routers/
    └── export_router.py                           # 🆕 (导出接口)
```

### 前端新增文件

```
jaaz/react/src/
├── components/
│   └── canvas/
│       ├── DocumentCard.tsx                       # 🆕
│       └── DocumentCardOverlay.tsx                # 🆕 (可选，备用方案)
│
└── api/
    └── export.ts                                  # 🆕 (导出 API 封装)
```

---

## 实施步骤

### Phase 1: 后端 Agent 系统（3-4天）

**Day 1: Agent 配置**
- [ ] 创建 4 个 Agent 配置文件
- [ ] 编写 System Prompt
- [ ] 测试 Agent Prompt 质量（使用 LLM Playground）

**Day 2: AgentManager 改造**
- [ ] 修改 `agent_manager.py`，新增 `mode` 参数
- [ ] 实现 `_create_course_agents` 方法
- [ ] 单元测试：验证两种模式 Agent 都能正常创建

**Day 3: 工具函数实现**
- [ ] 实现 `define_project_foundation`
- [ ] 实现 `design_assessment_framework`
- [ ] 实现 `generate_learning_blueprint`
- [ ] 实现 `export_course_markdown`
- [ ] 测试工具函数的 WebSocket 推送

**Day 4: 集成测试**
- [ ] 修改 `chat_service.py` 和 `agent_service.py`
- [ ] 端到端测试：从用户输入到 Agent 执行到工具调用
- [ ] 调试流式响应

---

### Phase 2: 前端画布与文档卡片（2-3天）

**Day 1: 模式选择界面**
- [ ] 修改首页，添加模式选择
- [ ] 将 `mode` 参数传递到后端 API
- [ ] 测试模式切换

**Day 2: 文档卡片组件**
- [ ] 创建 `DocumentCard` 组件
- [ ] 实现 Markdown 渲染
- [ ] 实现折叠/展开功能
- [ ] 实现编辑功能

**Day 3: 画布集成**
- [ ] 修改 `CanvasExcali.tsx`，监听 `add_document_card` 事件
- [ ] 实现文档卡片自动布局
- [ ] 测试多个卡片的渲染

---

### Phase 3: 导出功能（1-2天）

**Day 1: 后端导出逻辑**
- [ ] 实现 `/api/export/markdown` 接口
- [ ] 实现 Markdown 模板组织逻辑
- [ ] 测试文件生成和下载

**Day 2: 前端导出按钮**
- [ ] 在画布头部添加"导出"按钮
- [ ] 调用导出 API
- [ ] 触发文件下载

---

### Phase 4: 联调与优化（2-3天）

**Day 1-2: 完整流程测试**
- [ ] 端到端测试：从选择课程模式 → Agent 执行 → 文档卡片渲染 → 导出
- [ ] 测试多轮对话
- [ ] 测试错误处理

**Day 3: 体验优化**
- [ ] 优化文档卡片样式
- [ ] 优化 Agent 响应速度
- [ ] 添加加载动画和进度提示
- [ ] 优化错误提示

---

## 风险评估

### 风险 1: Excalidraw 的局限性

**问题**: Excalidraw 主要用于绘图，不适合展示大量文本内容

**影响**: 文档卡片可能与画布元素冲突

**解决方案**:
- 方案 A（推荐）: 文档卡片作为独立的 React 组件，覆盖在 Excalidraw 上层
- 方案 B: 考虑迁移到 tldraw（支持自定义节点）

**优先级**: 中

---

### 风险 2: Agent 生成质量不稳定

**问题**: LLM 生成的课程内容可能质量参差不齐

**影响**: 用户体验下降

**解决方案**:
- 优化 System Prompt，提供更多示例
- 在工具函数中增加验证逻辑
- 允许用户编辑文档卡片内容

**优先级**: 高

---

### 风险 3: 前端性能问题

**问题**: 多个文档卡片同时渲染可能影响性能

**影响**: 画布操作卡顿

**解决方案**:
- 实现虚拟滚动（只渲染可见的卡片）
- 使用 React.memo 优化组件渲染
- 延迟加载 Markdown 渲染

**优先级**: 低

---

## 总结

### 改造要点

1. **后端**：
   - ✅ 新增 4 个 UBD Agent 配置
   - ✅ 修改 AgentManager 支持模式切换
   - ✅ 新增 3 个 UBD 工具函数 + 1 个导出工具
   - ✅ 保留原有图像/视频功能

2. **前端**：
   - ✅ 新增模式选择界面
   - ✅ 新增文档卡片组件
   - ✅ 集成文档卡片到 Excalidraw 画布
   - ✅ 新增 Markdown 导出功能

3. **关键决策**：
   - ✅ 用户手动选择模式（准确性优先）
   - ✅ 文档卡片作为独立 React 组件覆盖在画布上
   - ✅ 保留 Excalidraw（不迁移到 tldraw）

### 预估工作量

- **后端**: 3-4 天
- **前端**: 2-3 天
- **联调**: 2-3 天
- **总计**: **7-10 天**

### 验收标准

- [ ] 用户可以选择"设计模式"或"课程模式"
- [ ] 课程模式下，Agent 能按顺序生成：项目基础 → 评估框架 → 学习蓝图
- [ ] 每个阶段的内容以文档卡片形式显示在画布上
- [ ] 文档卡片支持折叠、展开、编辑
- [ ] 用户可以导出完整的 Markdown 课程方案
- [ ] 原有图像/视频生成功能正常运行

---

**下一步建议**:

1. **立即启动 Phase 1**（后端 Agent 系统）
2. **前端同学并行开发模式选择界面**
3. **1 周内完成 MVP，进入测试阶段**

---

**文档版本**: v1.0
**最后更新**: 2025-10-05
**设计者**: Claude Code (Linus Mode)
