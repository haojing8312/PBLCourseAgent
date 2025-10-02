# 架构对齐 - 回归Phase 2原始设计

## ❌ 当前问题

在实现分阶段人工参与式工作流时，我**过度简化**了UI，去掉了核心的**无限画布**架构，这偏离了Phase 2的产品愿景。

**错误的实现**:
```
当前CourseDesignPage.tsx (658行)
├── Header (进度指示器)
├── Main Content (纯滚动式表单)
│   ├── 阶段1面板
│   ├── 阶段2面板
│   └── 阶段3面板
└── 没有画布，没有可视化
```

## ✅ 正确的架构

**Phase 2 原始愿景** (基于 tldraw + assistant-ui):

```
CourseDesignPage (正确版本)
├── Header (顶部工具栏)
├── Main Layout (flex布局)
│   ├── Left: 无限画布 (70%)
│   │   ├── 中心节点: "课程主任务"
│   │   ├── 子节点1: "阶段1-项目基础" (可编辑)
│   │   ├── 子节点2: "阶段2-评估框架" (可编辑)
│   │   └── 子节点3: "阶段3-学习蓝图" (可编辑)
│   └── Right: AI对话侧边栏 (30%)
│       ├── 用户输入
│       ├── AI流式响应
│       └── 阶段切换控制
└── 节点双击 → 打开编辑Modal
```

---

## 🎨 交互设计

### 1. 画布节点系统

**主任务节点** (中心):
```
┌─────────────────────────────┐
│  📚 AI绘画艺术探索课程       │
│                             │
│  年龄: 14-16岁              │
│  时长: 4天                  │
│  [开始工作流]               │
└─────────────────────────────┘
```

**阶段节点** (环绕主节点):
```
┌─────────────────┐      ┌─────────────────┐
│ 📋 阶段1        │──────│ 📊 阶段2        │
│ 项目基础定义     │      │ 评估框架设计     │
│                 │      │                 │
│ Status: ✅      │      │ Status: 🔄      │
│ [查看] [编辑]   │      │ [生成中...]     │
└─────────────────┘      └─────────────────┘
           │
           │
    ┌─────────────────┐
    │ 📅 阶段3        │
    │ 学习蓝图生成     │
    │                 │
    │ Status: ⏸️      │
    │ [等待阶段2]     │
    └─────────────────┘
```

### 2. AI对话侧边栏

```
┌────────────────────────────┐
│ 🤖 AI助手                  │
├────────────────────────────┤
│                            │
│ 助手: 准备开始生成阶段1吗？ │
│                            │
│ [开始生成阶段1]            │
│                            │
│ 用户: 开始                 │
│                            │
│ 助手: [流式生成中...]      │
│ ## 驱动性问题              │
│ 如何用AI...                │
│                            │
│ [✅ 完成] [🔄 重新生成]   │
│                            │
├────────────────────────────┤
│ 💬 输入消息...             │
└────────────────────────────┘
```

### 3. 工作流程

1. **初始状态**: 画布只有主任务节点
2. **点击"开始工作流"** → 右侧Chat显示阶段1提示
3. **用户确认** → AI开始生成（流式显示在Chat）
4. **生成完成** → 画布自动创建"阶段1节点"
5. **用户双击节点** → 打开编辑Modal
6. **保存编辑** → 节点标记为✅
7. **Chat提示"继续阶段2?"** → 用户确认 → 重复流程

---

## 🔧 技术实现要点

### 画布集成
```typescript
// 使用tldraw的自定义形状
import { createShapeId, Editor } from 'tldraw'

// 创建阶段节点
const createStageNode = (editor: Editor, stage: number, position: {x, y}) => {
  const shapeId = createShapeId()
  editor.createShape({
    id: shapeId,
    type: 'geo',
    x: position.x,
    y: position.y,
    props: {
      w: 200,
      h: 150,
      geo: 'rectangle',
      text: `阶段${stage}: 项目基础定义`,
      color: stage === 1 ? 'blue' : 'grey'
    }
  })
  return shapeId
}
```

### Chat流式显示
```typescript
// 使用EventSource接收SSE
const eventSource = new EventSource('/api/v1/generate/stage3/stream')

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (!data.done) {
    // 逐字追加到Chat
    setChatContent(prev => prev + data.chunk)
  } else {
    // 完成，创建画布节点
    createStageNode(editor, 3, {x: 400, y: 0})
    eventSource.close()
  }
}
```

### 节点编辑Modal
```typescript
// 双击节点打开Modal
const handleNodeDoubleClick = (nodeId: string) => {
  const nodeData = getNodeData(nodeId)
  setEditingNode({
    id: nodeId,
    stage: nodeData.stage,
    content: nodeData.content
  })
  setShowEditModal(true)
}

// Modal保存后更新节点
const saveNodeEdit = (newContent: string) => {
  updateNodeContent(editingNode.id, newContent)
  updateStageData(editingNode.stage, newContent)
  setShowEditModal(false)
}
```

---

## 📝 重构任务清单

### 1. 恢复InfiniteCanvas组件
- [x] 检查 `InfiniteCanvas.tsx` 是否还能用
- [ ] 添加节点创建/更新/删除方法
- [ ] 实现节点双击事件监听

### 2. 整合ChatSidebar
- [ ] 右侧固定宽度侧边栏
- [ ] 集成流式SSE接收
- [ ] 添加阶段控制按钮

### 3. 重构CourseDesignPage
- [ ] 左右分栏布局（画布 + Chat）
- [ ] 移除当前的表单式面板
- [ ] 添加节点编辑Modal
- [ ] 实现工作流状态机

### 4. 数据流设计
```typescript
interface CanvasNode {
  id: string
  type: 'main' | 'stage1' | 'stage2' | 'stage3'
  position: {x: number, y: number}
  status: 'pending' | 'generating' | 'completed' | 'editing'
  content: string
  editedContent?: string
}

interface WorkflowState {
  currentStage: 0 | 1 | 2 | 3  // 0=未开始, 1-3=各阶段
  nodes: CanvasNode[]
  chatHistory: ChatMessage[]
}
```

---

## ⚠️ 风险评估

### Linus式审查

**问题1: 过度设计？**
- ❌ 不是。这是Phase 2的核心产品定位
- ✅ 无限画布是差异化特性（vs 传统表单）

**问题2: 技术可行性？**
- ✅ tldraw已集成在package.json
- ✅ SSE流式已实现在后端
- ⚠️ 需要验证tldraw 4.0 API兼容性

**问题3: 用户价值？**
- ✅ 空间可视化：用户看到课程"图谱"
- ✅ 灵活编辑：随时回到任意节点修改
- ✅ 协作友好：未来可多人同时编辑画布

---

## 🚀 实施计划

### Phase 1: 验证画布功能 (30分钟)
1. 检查InfiniteCanvas组件是否正常渲染
2. 测试创建简单节点
3. 验证tldraw 4.0 API

### Phase 2: 集成Chat侧边栏 (1小时)
1. 右侧固定布局
2. 接入现有的ChatSidebar组件
3. 添加阶段控制逻辑

### Phase 3: 实现工作流 (2小时)
1. 阶段1: Chat生成 → 创建画布节点
2. 阶段2: 使用编辑后的阶段1数据
3. 阶段3: 使用编辑后的阶段1+2数据

### Phase 4: 节点编辑 (1小时)
1. 双击节点打开Modal
2. 显示当前内容
3. 保存编辑 → 更新画布节点样式

---

## 💡 产品愿景对齐

**Phase 2的核心价值**:
> "基于tldraw + assistant-ui的现代AI Agent架构，支持画布快照和结构化文档导出"

当前简化版**失去了**:
- ❌ 空间可视化能力
- ❌ tldraw的核心价值
- ❌ 与传统表单的差异化

**恢复后将获得**:
- ✅ 课程结构的空间表达
- ✅ 灵活的节点编辑体验
- ✅ 画布快照导出（PNG/SVG）
- ✅ 为Phase 3打好基础（多人协作）

---

**结论**: 需要立即重构回画布架构，这不是可选项，而是产品定位的核心。