# PBLCourseAgent Phase 2 详细开发计划

**制定时间:** 2025-09-29
**执行原则:** 分阶段、可测试、渐进式
**质量标准:** 每阶段完成后必须通过单元测试

---

## 🎯 总体目标回顾

将现有的表单式课程生成器转换为**任务驱动的无限画布**架构，采用tldraw + assistant-ui技术栈，实现：
- 无限画布上的可视化任务节点
- 实时AI对话与节点内容同步
- 智能工作流生成和管理
- 多格式导出功能

---

## 📋 阶段划分与里程碑

### Phase 2.1: 基础架构搭建 (预计2-3周)
**目标**: 建立前端技术栈和基础画布

#### 里程碑 M2.1
- [ ] React 18 + TypeScript + Vite 项目搭建
- [ ] tldraw 基础画布集成
- [ ] assistant-ui 基础对话组件集成
- [ ] Zustand 状态管理架构
- [ ] 基础布局：画布 + 侧边栏

#### 验收标准
- [ ] 可以在画布上添加基础形状
- [ ] 侧边栏可以显示简单的对话界面
- [ ] 前后端可以通信
- [ ] 所有组件有基础单元测试

### Phase 2.2: 自定义节点系统 (预计2-3周)
**目标**: 实现课程设计任务节点

#### 里程碑 M2.2
- [ ] 自定义TaskNode组件开发
- [ ] 四种节点类型实现：基础定义、评估框架、学习蓝图、资源创建
- [ ] 节点状态管理：待开始、进行中、已完成、错误
- [ ] 节点-对话交互机制
- [ ] 节点内容的流式更新

#### 验收标准
- [ ] 可以在画布上创建和编辑任务节点
- [ ] 点击节点可以切换对话上下文
- [ ] AI响应可以实时更新节点内容
- [ ] 节点状态变化正确显示

### Phase 2.3: 工作流引擎与同步 (预计2-3周)
**目标**: 实现智能任务编排和状态同步

#### 里程碑 M2.3
- [ ] 工作流自动生成算法
- [ ] 节点依赖关系可视化
- [ ] 任务进度追踪系统
- [ ] 流式内容同步引擎
- [ ] 错误处理和重试机制

#### 验收标准
- [ ] 根据用户输入可以自动生成工作流
- [ ] 节点间依赖关系正确显示
- [ ] 整体进度可以准确计算
- [ ] 异常情况有完善的处理

### Phase 2.4: 导出与优化 (预计1-2周)
**目标**: 完善导出功能和性能优化

#### 里程碑 M2.4
- [ ] 画布快照导出(PNG/SVG)
- [ ] 结构化文档导出(DOCX/PDF)
- [ ] 中文字体支持优化
- [ ] 性能优化和错误处理
- [ ] Docker容器化完善

#### 验收标准
- [ ] 可以导出高质量的画布图片
- [ ] 可以生成格式正确的Word/PDF文档
- [ ] 中文内容显示正常
- [ ] 支持20+节点的流畅操作

---

## 🛠️ Phase 2.1 详细实施方案

### 步骤1: 前端项目重构 (3-4天)

#### 1.1 创建新的前端目录结构
```bash
cd frontend
rm -rf * # 清空现有内容
mkdir -p src/{components,stores,types,utils,hooks}
```

#### 1.2 初始化Vite + React + TypeScript项目
```bash
npm create vite@latest . -- --template react-ts
npm install
```

#### 1.3 安装核心依赖
```bash
# 核心UI框架
npm install tldraw @assistant-ui/react

# 状态管理
npm install zustand

# 样式和工具
npm install tailwindcss @types/node

# 开发工具
npm install -D @types/react @types/react-dom eslint prettier
```

#### 1.4 配置TypeScript和构建工具
- 配置tsconfig.json
- 配置tailwind.config.js
- 配置vite.config.ts

### 步骤2: 基础布局组件开发 (2-3天)

#### 2.1 主应用布局
```typescript
// src/App.tsx
interface LayoutProps {
  canvas: React.ReactNode
  sidebar: React.ReactNode
  taskPanel: React.ReactNode
}

const AppLayout: React.FC<LayoutProps> = ({ canvas, sidebar, taskPanel }) => {
  return (
    <div className="h-screen flex">
      <div className="w-64 bg-gray-100">{taskPanel}</div>
      <div className="flex-1">{canvas}</div>
      <div className="w-80 bg-white border-l">{sidebar}</div>
    </div>
  )
}
```

#### 2.2 画布组件集成
```typescript
// src/components/Canvas/InfiniteCanvas.tsx
import { Tldraw } from 'tldraw'

export const InfiniteCanvas: React.FC = () => {
  return (
    <div className="w-full h-full">
      <Tldraw />
    </div>
  )
}
```

#### 2.3 对话侧边栏集成
```typescript
// src/components/Sidebar/ChatSidebar.tsx
import { AssistantProvider } from '@assistant-ui/react'

export const ChatSidebar: React.FC = () => {
  return (
    <div className="h-full p-4">
      <AssistantProvider>
        {/* 基础对话界面 */}
      </AssistantProvider>
    </div>
  )
}
```

### 步骤3: 状态管理架构 (2天)

#### 3.1 画布状态存储
```typescript
// src/stores/canvasStore.ts
import { create } from 'zustand'

interface CanvasState {
  selectedNodeId: string | null
  nodes: Map<string, TaskNode>
  connections: Connection[]
  setSelectedNode: (id: string | null) => void
  addNode: (node: TaskNode) => void
  updateNode: (id: string, updates: Partial<TaskNode>) => void
}

export const useCanvasStore = create<CanvasState>((set) => ({
  selectedNodeId: null,
  nodes: new Map(),
  connections: [],
  setSelectedNode: (id) => set({ selectedNodeId: id }),
  addNode: (node) => set((state) => ({
    nodes: new Map(state.nodes).set(node.id, node)
  })),
  updateNode: (id, updates) => set((state) => {
    const newNodes = new Map(state.nodes)
    const existing = newNodes.get(id)
    if (existing) {
      newNodes.set(id, { ...existing, ...updates })
    }
    return { nodes: newNodes }
  })
}))
```

#### 3.2 对话状态存储
```typescript
// src/stores/chatStore.ts
interface ChatState {
  messages: Message[]
  currentContext: TaskContext | null
  isStreaming: boolean
  addMessage: (message: Message) => void
  setContext: (context: TaskContext) => void
}
```

### 步骤4: 后端API扩展 (2-3天)

#### 4.1 新增流式API接口
```python
# backend/app/api/canvas_routes.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/canvas")

@router.post("/workflow/generate")
async def generate_workflow(input_data: WorkflowInput):
    """根据用户输入生成工作流节点"""
    pass

@router.post("/node/{node_id}/chat")
async def stream_node_chat(node_id: str, message: str):
    """节点相关的流式对话"""
    return StreamingResponse(
        stream_node_response(node_id, message),
        media_type="text/event-stream"
    )
```

#### 4.2 工作流生成服务
```python
# backend/app/services/workflow_service.py
class WorkflowGenerationService:
    async def generate_nodes_from_input(self, input_data: dict) -> List[TaskNode]:
        """根据用户输入智能生成任务节点"""
        # 分析用户输入
        # 生成节点图谱
        # 计算依赖关系
        pass
```

### 步骤5: 集成测试与验证 (1-2天)

#### 5.1 组件单元测试
```typescript
// src/components/__tests__/InfiniteCanvas.test.tsx
import { render, screen } from '@testing-library/react'
import { InfiniteCanvas } from '../Canvas/InfiniteCanvas'

describe('InfiniteCanvas', () => {
  it('should render tldraw canvas', () => {
    render(<InfiniteCanvas />)
    // 验证画布渲染
  })
})
```

#### 5.2 状态管理测试
```typescript
// src/stores/__tests__/canvasStore.test.ts
import { useCanvasStore } from '../canvasStore'

describe('canvasStore', () => {
  it('should manage node state correctly', () => {
    // 测试状态管理逻辑
  })
})
```

#### 5.3 API集成测试
```python
# backend/app/tests/test_canvas_api.py
def test_workflow_generation():
    """测试工作流生成API"""
    pass

def test_node_chat_streaming():
    """测试节点对话流式API"""
    pass
```

---

## ⚠️ 风险与应对策略

### 技术风险
1. **tldraw自定义shape复杂度**
   - 风险：自定义节点开发比预期复杂
   - 应对：先实现简单节点，逐步增加功能

2. **assistant-ui集成困难**
   - 风险：与现有后端API集成有兼容性问题
   - 应对：创建适配层，逐步迁移

3. **状态同步复杂度**
   - 风险：画布和对话状态同步出现bug
   - 应对：完善测试覆盖，建立清晰的数据流

### 时间风险
1. **学习曲线陡峭**
   - 应对：预留额外时间用于技术学习
   - 应对：分阶段验证，及时调整

2. **集成复杂度超预期**
   - 应对：优先实现核心功能，非关键功能可延后

---

## 📊 进度跟踪

### Phase 2.1 检查清单
- [ ] 前端项目搭建完成
- [ ] 基础画布可正常显示
- [ ] 对话组件可正常使用
- [ ] 状态管理正常工作
- [ ] 前后端通信正常
- [ ] 基础单元测试通过
- [ ] 代码质量检查通过

### 每日进度记录
| 日期 | 完成任务 | 遇到问题 | 解决方案 | 明日计划 |
|------|----------|----------|----------|----------|
| 2025-09-29 | 制定开发计划 | - | - | 开始前端重构 |

---

**说明**: 此计划将根据实际开发进度和遇到的技术问题进行动态调整。每个阶段完成后都会进行全面的测试验证，确保代码质量和功能完整性。