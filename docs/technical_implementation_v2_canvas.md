# Project Genesis AI - 第二阶段技术实现方案 (Canvas-Centered)

**文档版本:** 2.0
**创建日期:** 2025-09-29
**基于:** PRD v2.2 - Task-Driven Infinite Canvas
**架构理念:** 画布中心，节点驱动，对话辅助

---

## 1. 技术架构总览

### 1.1 核心设计理念
采用现代AI Agent产品的主流架构模式（Flowise.ai、Lovart等），以**无限画布为中心**，将课程设计任务可视化为**节点工作流**，通过**侧边栏对话**提供AI支持。

### 1.2 架构分层
```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                              │
├─────────────────────────────────────────────────────────┤
│  无限画布 (tldraw)  │  对话侧边栏 (assistant-ui)  │  任务面板   │
├─────────────────────────────────────────────────────────┤
│                  状态管理层 (Zustand)                      │
├─────────────────────────────────────────────────────────┤
│              节点引擎  │  工作流引擎  │  同步引擎              │
├─────────────────────────────────────────────────────────┤
│                  API通信层 (SSE + REST)                   │
├─────────────────────────────────────────────────────────┤
│                  后端服务层 (FastAPI)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 前端技术架构

### 2.1 目录结构重构
```
frontend/
├── src/
│   ├── components/
│   │   ├── Canvas/                    # 画布相关组件
│   │   │   ├── InfiniteCanvas.tsx     # tldraw无限画布
│   │   │   ├── TaskNode.tsx           # 任务节点组件
│   │   │   ├── ConnectionLine.tsx     # 连接线组件
│   │   │   └── CanvasToolbar.tsx      # 画布工具栏
│   │   ├── Sidebar/                   # 侧边栏组件
│   │   │   ├── ChatSidebar.tsx        # 对话侧边栏
│   │   │   ├── TaskPanel.tsx          # 任务面板
│   │   │   └── ProgressTracker.tsx    # 进度追踪
│   │   ├── Nodes/                     # 节点类型组件
│   │   │   ├── ProjectFoundationNode.tsx
│   │   │   ├── AssessmentNode.tsx
│   │   │   ├── LearningBlueprintNode.tsx
│   │   │   └── ResourceNode.tsx
│   │   └── Export/                    # 导出功能
│   │       ├── CanvasExporter.tsx
│   │       └── DocumentExporter.tsx
│   ├── engines/
│   │   ├── nodeEngine.ts              # 节点管理引擎
│   │   ├── workflowEngine.ts          # 工作流引擎
│   │   └── syncEngine.ts              # 状态同步引擎
│   ├── stores/
│   │   ├── canvasStore.ts             # 画布状态
│   │   ├── nodeStore.ts               # 节点状态
│   │   ├── chatStore.ts               # 对话状态
│   │   └── workflowStore.ts           # 工作流状态
│   └── types/
│       ├── node.ts                    # 节点类型定义
│       ├── workflow.ts                # 工作流类型
│       └── canvas.ts                  # 画布类型
```

### 2.2 核心技术选型
| 组件 | 技术选择 | 版本 | 用途 |
|------|----------|------|------|
| 无限画布 | tldraw | 4.0+ | 核心画布功能 |
| AI对话 | assistant-ui | latest | 流式对话组件 |
| 状态管理 | Zustand | 4.x | 轻量级状态管理 |
| 前端框架 | React 18 + TypeScript | 18.x | 基础框架 |
| 构建工具 | Vite | 5.x | 开发和构建 |
| 样式方案 | Tailwind CSS | 3.x | 原子化CSS |

### 2.3 tldraw 画布集成

#### 核心画布组件
```tsx
// InfiniteCanvas.tsx
import { Tldraw, TldrawEditor, createTLStore } from 'tldraw'
import { TaskNodeShapeUtil } from './shapes/TaskNodeShape'

const customShapeUtils = [TaskNodeShapeUtil]

export const InfiniteCanvas: React.FC = () => {
  const store = useMemo(() => createTLStore({
    shapeUtils: customShapeUtils,
  }), [])

  return (
    <div className="w-full h-screen">
      <Tldraw
        store={store}
        onMount={(editor) => {
          // 初始化画布，创建初始任务节点
          initializeWorkflow(editor)
        }}
      />
    </div>
  )
}
```

#### 自定义任务节点
```tsx
// TaskNodeShape.ts
import { BaseBoxShapeUtil, TLBaseShape } from 'tldraw'

export type TaskNodeShape = TLBaseShape<
  'task-node',
  {
    taskId: string
    title: string
    status: 'pending' | 'in_progress' | 'completed' | 'error'
    content?: string
    taskType: 'foundation' | 'assessment' | 'blueprint' | 'resource'
  }
>

export class TaskNodeShapeUtil extends BaseBoxShapeUtil<TaskNodeShape> {
  static override type = 'task-node' as const

  // 自定义节点渲染
  component(shape: TaskNodeShape) {
    return <TaskNodeComponent shape={shape} />
  }

  // 自定义节点指示器
  indicator(shape: TaskNodeShape) {
    return <TaskNodeIndicator shape={shape} />
  }
}
```

---

## 3. 状态管理架构

### 3.1 Zustand 状态设计

#### 画布状态管理
```typescript
// canvasStore.ts
interface CanvasState {
  // 画布状态
  viewport: { x: number; y: number; zoom: number }
  selectedNodeId: string | null

  // 节点管理
  nodes: Map<string, TaskNode>
  connections: Connection[]

  // 操作方法
  addNode: (node: TaskNode) => void
  updateNode: (id: string, updates: Partial<TaskNode>) => void
  selectNode: (id: string) => void
  deleteNode: (id: string) => void
}

export const useCanvasStore = create<CanvasState>((set, get) => ({
  // 初始状态
  viewport: { x: 0, y: 0, zoom: 1 },
  selectedNodeId: null,
  nodes: new Map(),
  connections: [],

  // 操作实现
  addNode: (node) => set((state) => ({
    nodes: new Map(state.nodes).set(node.id, node)
  })),
  // ... 其他方法
}))
```

#### 工作流状态管理
```typescript
// workflowStore.ts
interface WorkflowState {
  // 工作流状态
  currentPhase: 'planning' | 'executing' | 'completed'
  taskQueue: string[]
  completedTasks: Set<string>

  // 进度跟踪
  totalTasks: number
  completedCount: number
  progress: number

  // 操作方法
  startTask: (taskId: string) => void
  completeTask: (taskId: string) => void
  calculateProgress: () => void
}
```

### 3.2 状态同步机制

#### 画布-对话同步引擎
```typescript
// syncEngine.ts
class CanvasChatSyncEngine {
  private canvasStore = useCanvasStore.getState()
  private chatStore = useChatStore.getState()

  // 节点点击 -> 对话上下文切换
  onNodeSelect(nodeId: string) {
    const node = this.canvasStore.nodes.get(nodeId)
    if (node) {
      this.chatStore.setContext({
        taskType: node.taskType,
        currentContent: node.content,
        suggestedPrompts: this.generatePrompts(node)
      })
    }
  }

  // AI回复 -> 节点内容更新
  onChatResponse(response: StreamChunk) {
    const selectedNode = this.canvasStore.selectedNodeId
    if (selectedNode && response.canvas_update) {
      this.canvasStore.updateNode(selectedNode, {
        content: response.canvas_update.content,
        status: response.canvas_update.status
      })
    }
  }

  // 生成节点相关提示
  private generatePrompts(node: TaskNode): string[] {
    const promptMap = {
      foundation: [
        "优化驱动性问题",
        "完善最终成果描述",
        "调整课程标题"
      ],
      assessment: [
        "添加评估维度",
        "设计检查点",
        "优化量规标准"
      ],
      // ... 其他类型
    }
    return promptMap[node.taskType] || []
  }
}
```

---

## 4. 后端服务架构

### 4.1 API 设计扩展

#### 工作流管理API
```python
# 新增工作流路由
@router.post("/workflow/initialize")
async def initialize_workflow(request: WorkflowInitRequest):
    """基于用户输入初始化任务工作流"""

@router.post("/workflow/node/{node_id}/execute")
async def execute_node_task(node_id: str, context: TaskContext):
    """执行特定节点任务"""

@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """获取工作流执行状态"""
```

#### 流式节点更新服务
```python
# 节点任务执行服务
class NodeTaskExecutor:
    async def execute_task_stream(self, node_id: str, task_type: str, context: dict):
        """流式执行节点任务"""
        agent = self.get_agent_for_task_type(task_type)

        async for chunk in agent.stream_execute(context):
            # 解析AI输出，提取结构化内容
            node_update = self.parse_node_update(chunk, node_id)

            yield {
                "type": "node_update",
                "node_id": node_id,
                "content": chunk,
                "structured_data": node_update,
                "status": self.determine_status(chunk)
            }

    def get_agent_for_task_type(self, task_type: str):
        """根据任务类型选择对应的Agent"""
        agent_map = {
            "foundation": self.project_foundation_agent,
            "assessment": self.assessment_framework_agent,
            "blueprint": self.learning_blueprint_agent,
            "resource": self.resource_generation_agent
        }
        return agent_map.get(task_type)
```

### 4.2 工作流引擎设计

#### 任务依赖管理
```python
class WorkflowEngine:
    def __init__(self):
        self.task_graph = TaskGraph()
        self.execution_state = ExecutionState()

    async def initialize_workflow(self, user_input: CourseInput) -> WorkflowDefinition:
        """智能生成任务工作流"""
        # 1. 分析用户输入
        analysis = await self.analyze_requirements(user_input)

        # 2. 生成任务节点
        nodes = self.generate_task_nodes(analysis)

        # 3. 构建依赖关系
        dependencies = self.build_dependencies(nodes)

        # 4. 计算节点位置
        layout = self.calculate_layout(nodes, dependencies)

        return WorkflowDefinition(
            nodes=nodes,
            dependencies=dependencies,
            layout=layout
        )

    def generate_task_nodes(self, analysis: RequirementAnalysis) -> List[TaskNode]:
        """生成任务节点"""
        base_nodes = [
            TaskNode(
                id="foundation",
                type="foundation",
                title="项目基础定义",
                description="定义驱动性问题、最终成果等",
                estimated_time=300,  # 5分钟
                prerequisites=[]
            ),
            TaskNode(
                id="assessment",
                type="assessment",
                title="评估框架设计",
                description="设计评估量规和检查点",
                estimated_time=240,
                prerequisites=["foundation"]
            ),
            TaskNode(
                id="blueprint",
                type="blueprint",
                title="学习蓝图生成",
                description="设计时间线和活动安排",
                estimated_time=360,
                prerequisites=["foundation", "assessment"]
            )
        ]

        # 根据课程复杂度添加资源节点
        if analysis.needs_resources:
            resource_nodes = self.generate_resource_nodes(analysis)
            base_nodes.extend(resource_nodes)

        return base_nodes
```

---

## 5. 节点-对话交互机制

### 5.1 上下文切换系统

#### 智能上下文管理
```typescript
// contextManager.ts
class TaskContextManager {
  private currentContext: TaskContext | null = null

  switchToNode(nodeId: string) {
    const node = useCanvasStore.getState().nodes.get(nodeId)
    if (!node) return

    this.currentContext = {
      nodeId,
      taskType: node.taskType,
      currentContent: node.content,
      dependencies: this.getDependencies(nodeId),
      suggestedActions: this.generateActions(node),
      relatedContent: this.getRelatedContent(nodeId)
    }

    // 更新对话上下文
    useChatStore.getState().setContext(this.currentContext)
  }

  private generateActions(node: TaskNode): Action[] {
    const actionMap = {
      foundation: [
        { id: 'optimize_question', label: '优化驱动性问题', prompt: '请帮我优化这个驱动性问题，使其更加引人深思' },
        { id: 'refine_outcome', label: '完善最终成果', prompt: '请帮我完善最终成果的描述，使其更具体可衡量' },
        { id: 'add_context', label: '添加背景信息', prompt: '请为这个项目添加相关的背景信息和动机' }
      ],
      assessment: [
        { id: 'add_dimension', label: '添加评估维度', prompt: '请为这个评估框架添加一个新的评估维度' },
        { id: 'refine_rubric', label: '优化量规标准', prompt: '请帮我优化这些量规标准，使其更加具体明确' },
        { id: 'add_checkpoint', label: '设置检查点', prompt: '请为这个学习过程设置适当的形成性评估检查点' }
      ]
      // ... 其他节点类型
    }
    return actionMap[node.taskType] || []
  }
}
```

### 5.2 流式内容渲染

#### 节点内容实时更新
```tsx
// TaskNodeComponent.tsx
const TaskNodeComponent: React.FC<{shape: TaskNodeShape}> = ({ shape }) => {
  const [content, setContent] = useState(shape.props.content || '')
  const [isStreaming, setIsStreaming] = useState(false)

  // 监听流式更新
  useEffect(() => {
    const unsubscribe = streamingService.subscribe(shape.props.taskId, (chunk) => {
      if (chunk.type === 'content_chunk') {
        setContent(prev => prev + chunk.content)
        setIsStreaming(true)
      } else if (chunk.type === 'stream_end') {
        setIsStreaming(false)
      }
    })

    return unsubscribe
  }, [shape.props.taskId])

  return (
    <div className={`task-node ${shape.props.status}`}>
      <div className="node-header">
        <span className="node-icon">{getNodeIcon(shape.props.taskType)}</span>
        <h3>{shape.props.title}</h3>
        {isStreaming && <StreamingIndicator />}
      </div>
      <div className="node-content">
        <MarkdownRenderer content={content} />
      </div>
      <div className="node-footer">
        <StatusBadge status={shape.props.status} />
        <ActionButtons nodeId={shape.props.taskId} />
      </div>
    </div>
  )
}
```

---

## 6. 文档导出架构

### 6.1 双模式导出系统

#### 画布快照导出
```typescript
// CanvasExporter.ts
class CanvasExporter {
  async exportAsImage(format: 'png' | 'svg', options: ExportOptions) {
    const editor = useTldrawEditor()

    if (format === 'svg') {
      // 导出SVG矢量格式
      return await editor.getSvg({
        bounds: options.bounds,
        scale: options.scale || 1,
        background: options.includeBackground
      })
    } else {
      // 导出PNG位图格式
      return await editor.getDataUrl({
        bounds: options.bounds,
        scale: options.scale || 2, // 高分辨率
        format: 'png'
      })
    }
  }

  async exportWorkflowDiagram() {
    // 特殊的工作流图导出，只包含节点和连线
    const nodes = useCanvasStore.getState().nodes
    const connections = useCanvasStore.getState().connections

    return await this.generateWorkflowSvg(nodes, connections)
  }
}
```

#### 结构化文档导出
```typescript
// DocumentExporter.ts
class DocumentExporter {
  async exportToDocx(): Promise<Blob> {
    const nodes = this.getOrderedNodes() // 按依赖顺序排列
    const htmlContent = this.nodesToHtml(nodes)

    // 使用 @turbodocx/html-to-docx
    const docxBuffer = await htmlToDocx(htmlContent, {
      decodeUnicode: true,
      lang: 'zh-CN',
      orientation: 'portrait',
      margins: { top: 1000, right: 1000, bottom: 1000, left: 1000 }
    })

    return new Blob([docxBuffer], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
  }

  private nodesToHtml(nodes: TaskNode[]): string {
    return nodes.map(node => `
      <div class="task-section">
        <h2>${node.title}</h2>
        <div class="task-content">
          ${this.markdownToHtml(node.content || '')}
        </div>
      </div>
    `).join('\n')
  }

  async exportToPdf(): Promise<Blob> {
    // 使用 react-pdf 或者 html-to-pdf 方案
    const htmlContent = this.nodesToHtml(this.getOrderedNodes())

    // 通过后端服务生成PDF
    const response = await fetch('/api/v1/export/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ htmlContent })
    })

    return await response.blob()
  }
}
```

---

## 7. 部署与集成架构

### 7.1 Docker容器化方案

#### 优化的Dockerfile
```dockerfile
# 多阶段构建 - 前端构建
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# 安装依赖并构建
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

# 生产运行阶段
FROM python:3.10-slim AS production

WORKDIR /app

# 安装系统依赖（包含tldraw导出需要的浏览器环境）
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# 设置Chromium环境变量
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# 安装Python依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建必要目录
RUN mkdir -p /app/exports /app/temp

# 环境变量
ENV PYTHONPATH=/app
ENV STATIC_FILES_DIR=/app/static

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 开发环境配置

#### 快速启动脚本
```bash
#!/bin/bash
# start-dev.sh

echo "🚀 启动 Project Genesis AI 开发环境"

# 检查依赖
check_dependencies() {
    if ! command -v node &> /dev/null; then
        echo "❌ 请先安装 Node.js"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        echo "❌ 请先安装 Python 3.10+"
        exit 1
    fi
}

# 启动后端
start_backend() {
    echo "📡 启动后端服务..."
    cd backend
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    else
        source .venv/bin/activate
    fi
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    cd ..
}

# 启动前端
start_frontend() {
    echo "🎨 启动前端服务..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..
}

# 主流程
check_dependencies
start_backend
start_frontend

echo "✅ 开发环境启动完成!"
echo "🌐 前端地址: http://localhost:5173"
echo "📡 后端地址: http://localhost:8001"
echo "📖 API文档: http://localhost:8001/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap 'kill $BACKEND_PID $FRONTEND_PID' INT
wait
```

---

## 8. 性能优化策略

### 8.1 画布性能优化

#### 大量节点渲染优化
```typescript
// 虚拟化渲染优化
class CanvasPerformanceOptimizer {
  private viewport = { x: 0, y: 0, width: 1920, height: 1080 }

  getVisibleNodes(allNodes: Map<string, TaskNode>): TaskNode[] {
    // 只渲染视窗内的节点
    return Array.from(allNodes.values()).filter(node =>
      this.isNodeInViewport(node, this.viewport)
    )
  }

  private isNodeInViewport(node: TaskNode, viewport: Viewport): boolean {
    const buffer = 100 // 缓冲区
    return (
      node.x + node.width > viewport.x - buffer &&
      node.x < viewport.x + viewport.width + buffer &&
      node.y + node.height > viewport.y - buffer &&
      node.y < viewport.y + viewport.height + buffer
    )
  }
}
```

### 8.2 状态更新优化

#### 批量更新机制
```typescript
// 防抖动的状态更新
class StateUpdateBatcher {
  private pendingUpdates = new Map<string, any>()
  private updateTimer: NodeJS.Timeout | null = null

  batchUpdate(nodeId: string, update: Partial<TaskNode>) {
    this.pendingUpdates.set(nodeId, {
      ...this.pendingUpdates.get(nodeId),
      ...update
    })

    if (this.updateTimer) {
      clearTimeout(this.updateTimer)
    }

    this.updateTimer = setTimeout(() => {
      this.flushUpdates()
    }, 16) // ~60fps
  }

  private flushUpdates() {
    const canvasStore = useCanvasStore.getState()

    this.pendingUpdates.forEach((update, nodeId) => {
      canvasStore.updateNode(nodeId, update)
    })

    this.pendingUpdates.clear()
    this.updateTimer = null
  }
}
```

---

## 9. 开发实施路线图

### 9.1 阶段划分

#### Phase 1: 核心画布架构 (2-3周)
- [ ] tldraw集成和自定义节点开发
- [ ] 基础状态管理架构
- [ ] 简单的节点-对话交互
- [ ] 基础工作流生成

#### Phase 2: 交互体验完善 (2-3周)
- [ ] 流式内容渲染优化
- [ ] 智能上下文切换
- [ ] 任务进度可视化
- [ ] 节点状态管理完善

#### Phase 3: 高级功能开发 (2-3周)
- [ ] 工作流引擎完善
- [ ] 多模式导出功能
- [ ] 性能优化和错误处理
- [ ] 用户体验细节打磨

#### Phase 4: 部署和文档 (1-2周)
- [ ] Docker容器化
- [ ] 部署脚本和文档
- [ ] 性能测试和优化
- [ ] 开源发布准备

### 9.2 关键里程碑

| 里程碑 | 目标 | 验收标准 |
|--------|------|----------|
| M1 | 基础画布交互 | 节点创建、选择、基础对话 |
| M2 | 流式内容同步 | 对话内容实时更新到节点 |
| M3 | 完整工作流 | 从输入到完整课程方案生成 |
| M4 | 导出功能 | 画布和文档导出正常工作 |
| M5 | 性能优化 | 支持20+节点流畅交互 |
| M6 | 部署就绪 | Docker一键部署成功 |

---

## 10. 风险评估与应对

### 10.1 技术风险

#### 高风险项
1. **tldraw性能瓶颈**
   - 风险：大量自定义节点影响画布性能
   - 应对：实现虚拟化渲染，优化节点复杂度

2. **状态同步复杂度**
   - 风险：画布、对话、工作流状态同步出错
   - 应对：设计清晰的状态流向，完善错误恢复

#### 中风险项
1. **自定义节点兼容性**
   - 风险：tldraw版本升级影响自定义节点
   - 应对：抽象节点接口，降低耦合

2. **导出功能稳定性**
   - 风险：复杂画布导出失败
   - 应对：分层导出策略，提供降级方案

---

**文档维护者:** Claude Code
**最后更新:** 2025-09-29
**审核状态:** 待审核