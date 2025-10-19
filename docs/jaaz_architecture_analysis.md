# Jaaz 架构深度解析与 PBLCourseAgent 借鉴指南

> **分析时间**: 2025-10-05
> **分析对象**: Jaaz 开源 AI 设计助手 (https://github.com/11cafe/jaaz)
> **目的**: 为 PBLCourseAgent Phase 2 无限画布架构提供参考

---

## 📋 目录

1. [整体架构概览](#整体架构概览)
2. [核心技术栈](#核心技术栈)
3. [详细实现流程](#详细实现流程)
4. [关键代码分析](#关键代码分析)
5. [对 PBLCourseAgent 的启示](#对-pblcourseagent-的启示)
6. [实施路线图](#实施路线图)

---

## 整体架构概览

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                               │
│  用户输入 → ChatTextarea → 创建 Canvas                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (React + TypeScript)               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Excalidraw  │  │ ChatInterface │  │  WebSocket   │       │
│  │  画布组件   │◄─┤   聊天组件    │◄─┤ (Socket.IO)  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │ WebSocket 双向通信
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   后端层 (FastAPI + Python)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  chat_service.py                                     │   │
│  │   ↓                                                  │   │
│  │  langgraph_multi_agent()  ← 核心编排器                │   │
│  │   ↓                                                  │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  LangGraph Swarm (Multi-Agent 协作)         │   │   │
│  │  │  ┌──────────────┐  ┌─────────────────────┐ │   │   │
│  │  │  │ Planner      │──→│ ImageVideoCreator   │ │   │   │
│  │  │  │ Agent        │  │ Agent               │ │   │   │
│  │  │  └──────────────┘  └─────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │   ↓                                                  │   │
│  │  StreamProcessor → WebSocket 实时推送                 │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI 服务层                                   │
│  ┌──────────┐  ┌───────────┐  ┌───────────────┐           │
│  │ OpenAI   │  │ Jaaz API  │  │ Ollama (本地)  │           │
│  │ GPT-4o   │  │ (多模型)  │  │ LLM           │           │
│  └──────────┘  └───────────┘  └───────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 核心特性

1. **多 Agent 协作**: 基于 LangGraph Swarm，实现 Planner 和 ImageVideoCreator 智能体的无缝切换
2. **流式响应**: 实时推送 AI 生成内容，提供即时反馈
3. **画布同步**: AI 生成的图像/视频自动添加到 Excalidraw 画布
4. **混合部署**: 支持云端 API（Jaaz/OpenAI）和本地模型（Ollama/ComfyUI）

---

## 核心技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | - | Web 框架，提供 RESTful API |
| **LangGraph** | 0.4.8 | Multi-Agent 编排框架 |
| **LangGraph Swarm** | 0.0.11 | Agent 群组协作 |
| **LangChain** | 0.3.x | LLM 抽象层 |
| **Socket.IO** | 5.13.0 | WebSocket 实时通信 |
| **SQLite** | - | 会话和消息存储 |
| **OpenAI SDK** | 1.109.1 | OpenAI API 调用 |
| **Ollama SDK** | 0.6.0 | 本地 LLM 调用 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 19.1.0 | UI 框架 |
| **TypeScript** | 5.8.3 | 类型安全 |
| **Vite** | 6.3.5 | 构建工具 |
| **Excalidraw** | 0.18.0 | 无限画布组件 |
| **tldraw** | 3.13.1 | 备用画布组件 |
| **Socket.IO Client** | - | WebSocket 客户端 |
| **TanStack Router** | - | 路由管理 |
| **Zustand** | - | 状态管理 |

---

## 详细实现流程

### 案例场景：生成猫猫治愈视频

**用户输入**: "生成一个猫猫治愈视频"

#### Step 1: 前端发送请求

**文件**: `react/src/routes/index.tsx`

```typescript
// 用户在首页输入
<ChatTextarea
  messages={[]}
  onSendMessages={(messages, configs) => {
    createCanvasMutation({
      name: '新画布',
      canvas_id: nanoid(),
      messages: [{ role: 'user', content: '生成一个猫猫治愈视频' }],
      session_id: nanoid(),
      text_model: configs.textModel,  // { model: 'gpt-4o', provider: 'openai' }
      tool_list: configs.toolList,     // [Imagen 4, Seedance v1, ...]
      system_prompt: localStorage.getItem('system_prompt')
    })
  }}
/>
```

**API 调用**: `react/src/api/canvas.ts`

```typescript
export const createCanvas = async (data: CreateCanvasRequest) => {
  // 1. 创建画布记录
  const canvasResponse = await httpClient.post('/api/canvas/create', {
    canvas_id: data.canvas_id,
    name: data.name
  })

  // 2. 发送聊天消息
  await httpClient.post('/api/chat', {
    messages: data.messages,
    session_id: data.session_id,
    canvas_id: data.canvas_id,
    text_model: data.text_model,
    tool_list: data.tool_list,
    system_prompt: data.system_prompt
  })

  return canvasResponse.data
}
```

---

#### Step 2: 后端接收与处理

**文件**: `server/routers/chat_router.py`

```python
from fastapi import APIRouter
from services.chat_service import handle_chat

router = APIRouter()

@router.post("/api/chat")
async def chat(data: Dict[str, Any]):
    """
    接收聊天请求，异步处理
    """
    await handle_chat(data)
    return {"status": "processing"}
```

**文件**: `server/services/chat_service.py:17`

```python
async def handle_chat(data: Dict[str, Any]) -> None:
    """
    核心聊天处理函数

    工作流:
    1. 解析请求数据
    2. 保存会话到数据库
    3. 启动 LangGraph Agent 任务
    4. 实时流式推送结果
    """
    # 提取参数
    messages = data.get('messages', [])
    session_id = data.get('session_id', '')
    canvas_id = data.get('canvas_id', '')
    text_model = data.get('text_model', {})
    tool_list = data.get('tool_list', [])
    system_prompt = data.get('system_prompt')

    # 首次消息，创建会话
    if len(messages) == 1:
        await db_service.create_chat_session(
            session_id,
            text_model.get('model'),
            text_model.get('provider'),
            canvas_id,
            messages[0].get('content')[:200]
        )

    # 保存用户消息
    await db_service.create_message(
        session_id,
        messages[-1].get('role', 'user'),
        json.dumps(messages[-1])
    )

    # 创建 LangGraph Agent 任务
    task = asyncio.create_task(langgraph_multi_agent(
        messages, canvas_id, session_id, text_model, tool_list, system_prompt
    ))

    # 注册任务（用于取消）
    add_stream_task(session_id, task)

    try:
        await task
    except asyncio.CancelledError:
        print(f"🛑 Session {session_id} cancelled")
    finally:
        remove_stream_task(session_id)
        # 通知前端完成
        await send_to_websocket(session_id, {'type': 'done'})
```

---

#### Step 3: LangGraph Multi-Agent 编排

**文件**: `server/services/langgraph_service/agent_service.py:78`

```python
async def langgraph_multi_agent(
    messages: List[Dict[str, Any]],
    canvas_id: str,
    session_id: str,
    text_model: ModelInfo,
    tool_list: List[ToolInfoJson],
    system_prompt: Optional[str] = None
) -> None:
    """
    多智能体编排核心函数

    流程:
    1. 修复消息历史（处理不完整的 tool_calls）
    2. 创建文本模型实例
    3. 创建 Agent 群组
    4. 创建 Swarm 编排器
    5. 流式处理并推送结果
    """
    try:
        # 1. 修复消息历史
        fixed_messages = _fix_chat_history(messages)

        # 2. 创建文本模型
        text_model_instance = _create_text_model(text_model)

        # 3. 创建 Agent 群组
        agents = AgentManager.create_agents(
            text_model_instance,
            tool_list,
            system_prompt or ""
        )
        agent_names = [agent.name for agent in agents]

        # 4. 获取上次活跃的 Agent（用于恢复对话）
        last_agent = AgentManager.get_last_active_agent(fixed_messages, agent_names)

        # 5. 创建 Swarm 编排器
        swarm = create_swarm(
            agents=agents,
            default_active_agent=last_agent if last_agent else agent_names[0]
        )

        # 6. 创建上下文
        context = {
            'canvas_id': canvas_id,
            'session_id': session_id,
            'tool_list': tool_list,
        }

        # 7. 流式处理
        processor = StreamProcessor(session_id, db_service, send_to_websocket)
        await processor.process_stream(swarm, fixed_messages, context)

    except Exception as e:
        await _handle_error(e, session_id)
```

**Agent 创建**: `server/services/langgraph_service/agent_manager.py:18`

```python
class AgentManager:
    @staticmethod
    def create_agents(
        model: Any,
        tool_list: List[ToolInfoJson],
        system_prompt: str = ""
    ) -> List[CompiledGraph]:
        """
        创建 Agent 群组

        返回:
        - Planner Agent: 规划任务步骤
        - ImageVideoCreator Agent: 执行图像/视频生成
        """
        # 过滤工具
        image_tools = [tool for tool in tool_list if tool.get('type') == 'image']
        video_tools = [tool for tool in tool_list if tool.get('type') == 'video']

        print(f"📸 图像工具: {image_tools}")
        print(f"🎬 视频工具: {video_tools}")

        # 创建 Planner Agent
        planner_config = PlannerAgentConfig()
        planner_agent = AgentManager._create_langgraph_agent(model, planner_config)

        # 创建 ImageVideoCreator Agent
        image_video_creator_config = ImageVideoCreatorAgentConfig(tool_list)
        image_video_creator_agent = AgentManager._create_langgraph_agent(
            model, image_video_creator_config
        )

        return [planner_agent, image_video_creator_agent]

    @staticmethod
    def _create_langgraph_agent(
        model: Any,
        config: BaseAgentConfig
    ) -> CompiledGraph:
        """
        创建单个 LangGraph Agent

        步骤:
        1. 创建 Handoff 工具（Agent 间切换）
        2. 获取业务工具（图像/视频生成）
        3. 使用 create_react_agent 创建 Agent
        """
        # 创建 Agent 切换工具
        handoff_tools = []
        for handoff in config.handoffs:
            handoff_tool = create_handoff_tool(
                agent_name=handoff['agent_name'],
                description=handoff['description'],
            )
            if handoff_tool:
                handoff_tools.append(handoff_tool)

        # 获取业务工具
        business_tools = []
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
```

---

#### Step 4: Agent 配置详解

**Planner Agent**: `server/services/langgraph_service/configs/planner_config.py:5`

```python
class PlannerAgentConfig(BaseAgentConfig):
    """
    规划智能体

    职责:
    1. 分析用户需求
    2. 制定执行计划（write_plan 工具）
    3. 移交给专业 Agent（transfer_to_image_video_creator）
    """
    def __init__(self) -> None:
        system_prompt = """
你是设计规划智能体。用户的语言是什么语言，你就用什么语言回答。

任务流程:
1. 如果是复杂任务，使用 write_plan 工具将任务分解为高级步骤
2. 如果是图像/视频生成任务，立即移交给 image_video_creator，无需用户批准

重要规则:
1. 必须先完成 write_plan 工具调用，等待结果后再切换 Agent
2. 不要同时调用多个工具
3. 始终等待一个工具调用完成后再调用下一个

注意图像数量:
- 如果用户指定数量（如"20张图片"），必须在计划中包含准确数量
- 切换到 image_video_creator 时，明确传达所需数量
- 永远不要忽略或修改用户指定的数量

示例计划（生成口红广告视频）:
[
  {
    "title": "设计视频脚本",
    "description": "为广告视频设计脚本"
  },
  {
    "title": "生成图像",
    "description": "设计图像提示词，生成故事板图像"
  },
  {
    "title": "生成视频片段",
    "description": "从图像生成视频片段"
  }
]
"""

        # 定义 Handoff（Agent 切换）
        handoffs = [{
            'agent_name': 'image_video_creator',
            'description': '移交给图像视频创作者。专门从文本或输入图像生成图像和视频。'
        }]

        super().__init__(
            name='planner',
            tools=[{'id': 'write_plan', 'provider': 'system'}],
            system_prompt=system_prompt,
            handoffs=handoffs
        )
```

**ImageVideoCreator Agent**: `server/services/langgraph_service/configs/image_vide_creator_config.py:46`

```python
class ImageVideoCreatorAgentConfig(BaseAgentConfig):
    """
    图像视频创作智能体

    职责:
    1. 编写设计策略文档
    2. 调用图像生成工具
    3. 调用视频生成工具
    """
    def __init__(self, tool_list: List[ToolInfoJson]) -> None:
        system_prompt = """
你是图像视频创作者。你可以从文本或图像创建图像或视频。
你能够编写专业的图像提示词，生成符合用户需求的美学图像。

1. 图像生成任务流程:
   - 先用与用户相同的语言编写设计策略文档

   示例设计策略文档:
   《MUSE MODULAR – 未来身份》封面设计方案

   • 推荐分辨率: 1024 × 1536 px（竖版）– 适合标准杂志尺寸，保留全息细节

   • 风格与氛围
   – 高对比度灰度基调，唤起永恒的编辑风格
   – 选择性应用全息彩虹色（青 → 紫 → 柠檬绿）于面具边缘、标题字形和微小故障，
     象征未来主义和流动身份
   – 氛围：神秘、智性、略带不安但魅力十足

   • 关键视觉元素
   – 中心雌雄同体模特，肩部以上，柔光正面照明 + 双侧轮廓光
   – 透明多边形 AR 面具覆盖面部；内部有三个偏移的"幽灵"面部层（不同的眼睛、
     鼻子、嘴巴）暗示多重人格
   – 微妙的像素排序/故障条纹从面具边缘散发，融入背景网格

   [更多详细设计元素...]

2. 根据计划立即调用 generate_image 工具生成图像，使用专业详细的图像提示词，
   无需征求用户批准

3. 视频生成任务:
   - 可以选择先生成必要的图像，然后使用图像生成视频
   - 或直接使用文本提示生成视频
"""

        # 输入图像检测提示
        image_input_detection_prompt = """
输入图像检测:
当用户消息包含 XML 格式的输入图像时:
<input_images></input_images>

你必须:
1. 解析 XML 提取 <image> 标签的 file_id 属性
2. 当存在图像时，使用支持 input_images 参数的工具
3. 将提取的 file_id 作为列表传递给 input_images 参数
4. 如果 input_images 数量 > 1，仅使用 generate_image_by_gpt_image_1_jaaz（支持多图）
5. 视频生成 → 如果存在图像，使用带 input_images 的视频工具
"""

        # 批量生成规则
        batch_generation_prompt = """
批量生成规则:
- 如果用户需要 >10 张图像: 每批最多生成 10 张
- 完成一批后再开始下一批
- 示例（20张图）: 批次1 (1-10) → "批次1完成!" → 批次2 (11-20) → "全部20张完成!"
"""

        # 错误处理指令
        error_handling_prompt = """
错误处理指令:
当图像生成失败时，你必须:
1. 承认失败并向用户解释具体原因
2. 如果错误提到"敏感内容"或"标记内容"，建议用户:
   - 使用更合适、更不敏感的描述
   - 避免潜在争议、暴力或不当内容
   - 尝试用更中性的语言重新表述
3. 如果是 API 错误 (HTTP 500等)，建议:
   - 稍后再试
   - 在提示中使用不同措辞
   - 检查服务是否暂时不可用
4. 始终为替代方法提供有用建议
5. 保持支持性和专业的语气

重要: 永远不要忽略工具错误。始终对失败的工具调用提供有用的指导。
"""

        full_system_prompt = (
            system_prompt +
            image_input_detection_prompt +
            batch_generation_prompt +
            error_handling_prompt
        )

        # 图像设计 Agent 不需要切换到其他 Agent
        handoffs = []

        super().__init__(
            name='image_video_creator',
            tools=tool_list,  # 动态注入所有可用工具
            system_prompt=full_system_prompt,
            handoffs=handoffs
        )
```

---

#### Step 5: 流式处理与实时推送

**文件**: `server/services/langgraph_service/StreamProcessor.py:20`

```python
class StreamProcessor:
    """
    流式处理器

    职责:
    1. 监听 LangGraph Swarm 的流式输出
    2. 实时推送 AI 响应到前端
    3. 保存消息到数据库
    """
    def __init__(self, session_id: str, db_service: Any, websocket_service: Callable):
        self.session_id = session_id
        self.db_service = db_service
        self.websocket_service = websocket_service
        self.tool_calls = []
        self.last_saved_message_index = 0

    async def process_stream(
        self,
        swarm: StateGraph,
        messages: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> None:
        """
        处理整个流式响应

        流程:
        1. 编译 Swarm
        2. 异步迭代流式输出
        3. 处理每个 chunk（文本/工具调用/完整消息）
        """
        self.last_saved_message_index = len(messages) - 1

        # 编译 Swarm
        compiled_swarm = swarm.compile()

        # 异步迭代流式输出
        async for chunk in compiled_swarm.astream(
            {"messages": messages},
            config=context,
            stream_mode=["messages", "custom", 'values']
        ):
            await self._handle_chunk(chunk)

        # 发送完成事件
        await self.websocket_service(self.session_id, {'type': 'done'})

    async def _handle_chunk(self, chunk: Any) -> None:
        """
        处理单个 chunk

        Chunk 类型:
        - messages: AI 文本响应或工具调用
        - values: 完整的消息列表（用于数据库保存）
        - custom: 自定义事件
        """
        chunk_type = chunk[0]

        if chunk_type == 'values':
            await self._handle_values_chunk(chunk[1])
        else:
            await self._handle_message_chunk(chunk[1][0])

    async def _handle_values_chunk(self, chunk_data: Dict[str, Any]) -> None:
        """
        处理 values 类型的 chunk

        作用:
        1. 将 LangChain 消息转换为 OpenAI 格式
        2. 发送所有消息到前端
        3. 保存新消息到数据库
        """
        all_messages = chunk_data.get('messages', [])
        oai_messages = convert_to_openai_messages(all_messages)

        # 确保是列表
        if not isinstance(oai_messages, list):
            oai_messages = [oai_messages] if oai_messages else []

        # 发送所有消息到前端
        await self.websocket_service(self.session_id, {
            'type': 'all_messages',
            'messages': oai_messages
        })

        # 保存新消息到数据库
        for i in range(self.last_saved_message_index + 1, len(oai_messages)):
            new_message = oai_messages[i]
            if len(oai_messages) > 0:
                await self.db_service.create_message(
                    self.session_id,
                    new_message.get('role', 'user'),
                    json.dumps(new_message)
                )
            self.last_saved_message_index = i

    async def _handle_message_chunk(self, ai_message_chunk: AIMessageChunk) -> None:
        """
        处理 message 类型的 chunk

        可能的内容:
        - 文本内容（AI 响应）
        - 工具调用（Tool Call）
        - 工具调用结果（Tool Message）
        """
        try:
            content = ai_message_chunk.content

            # 工具调用结果
            if isinstance(ai_message_chunk, ToolMessage):
                oai_message = convert_to_openai_messages([ai_message_chunk])[0]
                print('👇 工具调用结果:', oai_message)
                await self.websocket_service(self.session_id, {
                    'type': 'tool_call_result',
                    'id': ai_message_chunk.tool_call_id,
                    'message': oai_message
                })

            # 文本内容
            elif content:
                await self.websocket_service(self.session_id, {
                    'type': 'delta',
                    'text': content
                })

            # 工具调用
            elif (hasattr(ai_message_chunk, 'tool_calls') and
                  ai_message_chunk.tool_calls and
                  ai_message_chunk.tool_calls[0].get('name')):
                await self._handle_tool_calls(ai_message_chunk.tool_calls)

            # 工具调用参数流
            if hasattr(ai_message_chunk, 'tool_call_chunks'):
                await self._handle_tool_call_chunks(ai_message_chunk.tool_call_chunks)

        except Exception as e:
            print('🟠 错误:', e)
            traceback.print_stack()

    async def _handle_tool_calls(self, tool_calls: List[ToolCall]) -> None:
        """
        处理工具调用

        流程:
        1. 过滤有效的工具调用
        2. 检查是否需要用户确认
        3. 发送工具调用事件到前端
        """
        self.tool_calls = [tc for tc in tool_calls if tc.get('name')]
        print('😘 工具调用事件:', tool_calls)

        # 需要确认的工具列表（例如视频生成可能很慢/贵）
        TOOLS_REQUIRING_CONFIRMATION = {
            'generate_video_by_veo3_fast_jaaz',
        }

        for tool_call in self.tool_calls:
            tool_name = tool_call.get('name')

            # 检查是否需要确认
            if tool_name in TOOLS_REQUIRING_CONFIRMATION:
                print(f'🔄 工具 {tool_name} 需要确认，跳过自动推送')
                continue
            else:
                await self.websocket_service(self.session_id, {
                    'type': 'tool_call',
                    'id': tool_call.get('id'),
                    'name': tool_name,
                    'arguments': '{}'
                })
```

---

#### Step 6: 前端 WebSocket 接收与画布更新

**WebSocket 连接**: `react/src/contexts/socket.tsx:23`

```typescript
export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const socketManagerRef = useRef<SocketIOManager | null>(null)

  useEffect(() => {
    const initializeSocket = async () => {
      // 创建 Socket Manager
      if (!socketManagerRef.current) {
        socketManagerRef.current = new SocketIOManager({
          serverUrl: process.env.NODE_ENV === 'development'
            ? 'http://localhost:57988'
            : window.location.origin,
          autoConnect: false
        })
      }

      const socketManager = socketManagerRef.current
      await socketManager.connect()

      console.log('🚀 Socket.IO 初始化成功')

      // 监听连接事件
      const socket = socketManager.getSocket()
      if (socket) {
        socket.on('connect', () => setConnected(true))
        socket.on('disconnect', () => setConnected(false))
        socket.on('connect_error', (error) => setError(error.message))
      }
    }

    initializeSocket()

    return () => {
      if (socketManagerRef.current) {
        socketManagerRef.current.disconnect()
      }
    }
  }, [])

  return (
    <SocketContext.Provider value={{
      connected,
      socketManager: socketManagerRef.current
    }}>
      {children}
    </SocketContext.Provider>
  )
}
```

**聊天组件监听**: `react/src/components/chat/Chat.tsx`

```typescript
const ChatInterface = ({ canvasId, sessionId }) => {
  const { socketManager } = useSocket()
  const { excalidrawAPI } = useCanvas()

  useEffect(() => {
    if (!socketManager || !sessionId) return

    // 监听 AI 文本响应
    const handleDelta = (data: ISocket.StreamDelta) => {
      setStreamingText((prev) => prev + data.text)
    }

    // 监听工具调用
    const handleToolCall = (data: ISocket.ToolCall) => {
      console.log('🔧 工具调用:', data.name)
      setToolCalls((prev) => [...prev, data])
    }

    // 监听工具调用结果（最重要！）
    const handleToolResult = (data: ISocket.ToolCallResult) => {
      console.log('✅ 工具结果:', data)

      // 解析结果中的图像/视频 URL
      const imageMatch = data.message.content.match(/\(http:\/\/[^\)]+\)/)
      if (imageMatch) {
        const imageUrl = imageMatch[0].slice(1, -1)  // 去掉括号

        // 触发画布添加元素事件
        eventBus.emit('add-canvas-element', {
          type: 'image',
          url: imageUrl,
          file_id: data.id
        })
      }
    }

    // 监听完成事件
    const handleDone = () => {
      console.log('✨ 对话完成')
      setIsStreaming(false)
    }

    // 注册监听器
    socketManager.on('delta', handleDelta)
    socketManager.on('tool_call', handleToolCall)
    socketManager.on('tool_call_result', handleToolResult)
    socketManager.on('done', handleDone)

    return () => {
      socketManager.off('delta', handleDelta)
      socketManager.off('tool_call', handleToolCall)
      socketManager.off('tool_call_result', handleToolResult)
      socketManager.off('done', handleDone)
    }
  }, [socketManager, sessionId])

  return (
    <div className="chat-interface">
      {/* 聊天 UI */}
    </div>
  )
}
```

**画布组件更新**: `react/src/components/canvas/CanvasExcali.tsx:42`

```typescript
const CanvasExcali = ({ canvasId, initialData }) => {
  const { excalidrawAPI, setExcalidrawAPI } = useCanvas()
  const lastImagePositionRef = useRef<LastImagePosition>({
    x: 100,
    y: 100,
    width: 400,
    height: 300,
    col: 0
  })

  useEffect(() => {
    // 监听画布添加元素事件
    const handleAddElement = async (data: { type: string; url: string; file_id: string }) => {
      if (!excalidrawAPI || data.type !== 'image') return

      // 1. 下载图像并转换为 Excalidraw 文件格式
      const response = await fetch(data.url)
      const blob = await response.blob()
      const dataURL = await blobToDataURL(blob)

      const imageFile: BinaryFileData = {
        id: data.file_id,
        dataURL: dataURL,
        mimeType: 'image/png',
        created: Date.now()
      }

      // 2. 添加文件到 Excalidraw
      excalidrawAPI.addFiles([imageFile])

      // 3. 计算新图像位置（网格布局）
      const lastPos = lastImagePositionRef.current
      const newX = lastPos.x + (lastPos.col * (lastPos.width + 50))
      const newY = lastPos.y
      const newCol = (lastPos.col + 1) % 3  // 每行3张图

      // 如果换行
      const newYPos = newCol === 0 ? lastPos.y + lastPos.height + 50 : newY

      // 4. 创建 Excalidraw 图像元素
      const imageElement = convertToExcalidrawElements([{
        type: 'image',
        x: newX,
        y: newYPos,
        width: 400,
        height: 300,
        fileId: data.file_id
      }])

      // 5. 更新画布
      excalidrawAPI.updateScene({
        elements: [...excalidrawAPI.getSceneElements(), ...imageElement]
      })

      // 6. 更新位置记录
      lastImagePositionRef.current = {
        x: newX,
        y: newYPos,
        width: 400,
        height: 300,
        col: newCol
      }
    }

    eventBus.on('add-canvas-element', handleAddElement)

    return () => {
      eventBus.off('add-canvas-element', handleAddElement)
    }
  }, [excalidrawAPI])

  return (
    <Excalidraw
      ref={(api) => setExcalidrawAPI(api)}
      initialData={initialData}
      onChange={(elements, appState, files) => {
        // 自动保存画布状态（防抖）
        handleSave(elements, appState, files)
      }}
    />
  )
}
```

---

## 关键代码分析

### 1. Agent 切换机制 (Handoff)

**实现文件**: `server/services/langgraph_service/configs/base_config.py`

```python
from langchain_core.tools import StructuredTool

def create_handoff_tool(agent_name: str, description: str) -> StructuredTool:
    """
    创建 Agent 切换工具

    原理:
    LangGraph Swarm 会检测特定格式的工具调用，
    当检测到 transfer_to_{agent_name} 时，自动切换到目标 Agent

    参数:
    - agent_name: 目标 Agent 的名称
    - description: 切换原因描述（帮助 LLM 决定何时切换）

    返回:
    - StructuredTool: LangChain 工具对象
    """
    def transfer_fn() -> str:
        """切换函数（实际上只是返回一个信号）"""
        return f"Transfer to {agent_name}"

    return StructuredTool.from_function(
        func=transfer_fn,
        name=f"transfer_to_{agent_name}",
        description=description
    )
```

**工作流程**:
1. Planner Agent 完成规划后，LLM 决定调用 `transfer_to_image_video_creator`
2. LangGraph Swarm 检测到这个特殊的工具调用
3. Swarm 自动切换活跃 Agent 为 `image_video_creator`
4. ImageVideoCreator Agent 接收上下文并继续执行

---

### 2. 工具定义与画布同步

**工具注册**: `server/services/tool_service.py`

```python
class ToolService:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool_id: str, tool: BaseTool):
        """注册工具到服务"""
        self.tools[tool_id] = tool

    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tools.get(tool_id)

tool_service = ToolService()
```

**示例工具**: `server/tools/image_generation.py`

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class ImageGenerationInput(BaseModel):
    """图像生成工具输入"""
    prompt: str = Field(description="图像生成提示词")
    width: int = Field(default=1024, description="图像宽度")
    height: int = Field(default=1024, description="图像高度")

async def generate_image_by_imagen_4_jaaz(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    **kwargs
) -> str:
    """
    使用 Google Imagen 4 生成图像

    流程:
    1. 调用 Jaaz API 生成图像
    2. 下载图像并保存到本地
    3. 通过 WebSocket 推送画布更新事件
    4. 返回结果给 LLM
    """
    # 从上下文获取参数
    canvas_id = kwargs.get('canvas_id')
    session_id = kwargs.get('session_id')

    try:
        # 1. 调用 Jaaz API
        response = await jaaz_service.generate_image(
            model='google/imagen-4',
            prompt=prompt,
            width=width,
            height=height
        )

        image_url = response['data'][0]['url']

        # 2. 下载并保存图像
        file_id = await save_image_to_local(image_url)
        local_url = f'http://localhost:57988/api/file/{file_id}'

        # 3. 推送画布更新事件（关键！）
        await send_to_websocket(session_id, {
            'type': 'tool_call_result',
            'name': 'generate_image_by_imagen_4_jaaz',
            'id': file_id,
            'message': {
                'role': 'tool',
                'content': f'图像生成成功 ![{file_id}]({local_url})'
            }
        })

        # 4. 返回结果给 LLM（用于后续推理）
        return f"图像生成成功！图像ID: {file_id}"

    except Exception as e:
        # 错误处理
        error_msg = f"图像生成失败: {str(e)}"
        await send_to_websocket(session_id, {
            'type': 'error',
            'message': error_msg
        })
        return error_msg

# 注册工具
tool = StructuredTool.from_function(
    func=generate_image_by_imagen_4_jaaz,
    name='generate_image_by_imagen_4_jaaz',
    description='使用 Google Imagen 4 生成高质量图像',
    args_schema=ImageGenerationInput
)

tool_service.register_tool('generate_image_by_imagen_4_jaaz', tool)
```

---

### 3. 画布状态管理

**Context 提供者**: `react/src/contexts/canvas.tsx`

```typescript
import { createContext, useContext, useState, useEffect } from 'react'
import { ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types/types'
import { eventBus } from '@/lib/event'

interface CanvasContextType {
  excalidrawAPI: ExcalidrawImperativeAPI | null
  setExcalidrawAPI: (api: ExcalidrawImperativeAPI) => void
}

const CanvasContext = createContext<CanvasContextType>({
  excalidrawAPI: null,
  setExcalidrawAPI: () => {}
})

export const useCanvas = () => useContext(CanvasContext)

export const CanvasProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [excalidrawAPI, setExcalidrawAPI] = useState<ExcalidrawImperativeAPI | null>(null)

  useEffect(() => {
    // 监听画布添加元素事件
    const handleAddElement = (data: any) => {
      console.log('📢 收到画布添加元素事件:', data)
    }

    eventBus.on('add-canvas-element', handleAddElement)

    return () => {
      eventBus.off('add-canvas-element', handleAddElement)
    }
  }, [excalidrawAPI])

  return (
    <CanvasContext.Provider value={{ excalidrawAPI, setExcalidrawAPI }}>
      {children}
    </CanvasContext.Provider>
  )
}
```

**事件总线**: `react/src/lib/event.ts`

```typescript
import mitt, { Emitter } from 'mitt'

type Events = {
  'add-canvas-element': {
    type: 'image' | 'video' | 'text'
    url?: string
    file_id?: string
    content?: string
    position?: { x: number; y: number }
  }
  'update-canvas-element': {
    id: string
    updates: any
  }
  'delete-canvas-element': {
    id: string
  }
}

export const eventBus: Emitter<Events> = mitt<Events>()
```

---

## 对 PBLCourseAgent 的启示

### 架构相似度对比

| 维度 | Jaaz | PBLCourseAgent Phase 2 | 相似度 |
|------|------|----------------------|--------|
| **后端框架** | FastAPI + Python | FastAPI + Python | ✅ 100% |
| **Agent 框架** | LangGraph Swarm | (待实现) | ✅ 可直接复用 |
| **Agent 数量** | 2 (Planner + Creator) | 3 (Foundation + Assessment + Blueprint) | ⚠️ 需调整 |
| **前端框架** | React + TypeScript | React + TypeScript | ✅ 100% |
| **画布组件** | Excalidraw | tldraw | ⚠️ API 不同，逻辑相似 |
| **实时通信** | WebSocket (Socket.IO) | (待实现) | ✅ 可直接复用 |
| **数据流** | 流式响应 (astream) | (待实现) | ✅ 可直接复用 |

### 直接可复用的模块

#### ✅ 后端核心 (100% 可复用)

```
backend/
├── services/
│   ├── chat_service.py                    # ✅ 直接复用
│   ├── langgraph_service/
│   │   ├── agent_manager.py               # ✅ 直接复用
│   │   ├── agent_service.py               # ✅ 直接复用
│   │   ├── StreamProcessor.py             # ✅ 直接复用
│   │   └── configs/
│   │       ├── base_config.py             # ✅ 直接复用
│   │       ├── planner_config.py          # ⚠️ 需修改为 PBL Planner
│   │       └── image_vide_creator_config.py # ⚠️ 需修改为 Assessment/Blueprint
│   ├── websocket_service.py               # ✅ 直接复用
│   └── tool_service.py                    # ✅ 直接复用
```

#### ✅ 前端核心 (80% 可复用)

```
frontend-v2/
├── src/
│   ├── contexts/
│   │   ├── socket.tsx                     # ✅ 直接复用
│   │   └── canvas.tsx                     # ⚠️ 需修改为 tldraw API
│   ├── lib/
│   │   ├── socket.ts                      # ✅ 直接复用
│   │   └── event.ts                       # ✅ 直接复用
│   ├── components/
│   │   ├── chat/
│   │   │   └── Chat.tsx                   # ✅ 直接复用（逻辑）
│   │   └── canvas/
│   │       └── Canvas.tsx                 # ⚠️ 需改为 tldraw
│   └── routes/
│       └── canvas.$id.tsx                 # ✅ 布局逻辑可复用
```

---

### 需要调整的部分

#### 🔧 Agent 配置（重要！）

**你们的三 Agent 配置**:

1. **Project Foundation Agent**

```python
class ProjectFoundationAgentConfig(BaseAgentConfig):
    """
    项目基础定义智能体

    职责:
    1. 分析学生需求
    2. 定义项目主题
    3. 设定学习目标
    4. 移交给 Assessment Agent
    """
    def __init__(self):
        system_prompt = """
你是 PBL 项目基础定义专家。

任务:
1. 分析学生的学习需求和兴趣
2. 定义项目主题和核心问题
3. 设定清晰的学习目标（知识、技能、态度）
4. 完成后，移交给评估框架设计智能体

输出格式:
- 项目主题
- 核心驱动问题
- 学习目标列表
"""

        handoffs = [{
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

2. **Assessment Framework Agent**

```python
class AssessmentFrameworkAgentConfig(BaseAgentConfig):
    """
    评估框架设计智能体

    职责:
    1. 设计评估标准
    2. 创建评估量规
    3. 规划评估时间点
    4. 移交给 Blueprint Agent
    """
    def __init__(self):
        system_prompt = """
你是 PBL 评估框架设计专家。

任务:
1. 基于学习目标设计评估标准
2. 创建详细的评估量规（Rubric）
3. 规划形成性评估和总结性评估时间点
4. 完成后，移交给学习蓝图生成智能体

输出格式:
- 评估标准列表
- 评估量规表格
- 评估时间线
"""

        handoffs = [{
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

3. **Learning Blueprint Agent**

```python
class LearningBlueprintAgentConfig(BaseAgentConfig):
    """
    学习蓝图生成智能体

    职责:
    1. 设计学习活动序列
    2. 分配时间和资源
    3. 生成完整的课程蓝图
    4. 导出为结构化文档
    """
    def __init__(self):
        system_prompt = """
你是 PBL 学习蓝图设计专家。

任务:
1. 基于项目目标和评估框架，设计学习活动序列
2. 为每个活动分配时间、资源和评估节点
3. 生成完整的学习蓝图
4. 调用文档导出工具，生成最终课程方案

输出格式:
- 学习活动时间线
- 每个活动的详细描述
- 资源清单
- 评估节点标注
"""

        handoffs = []  # 最后一个 Agent，不需要切换

        super().__init__(
            name='blueprint_generator',
            tools=[
                {'id': 'generate_learning_blueprint', 'provider': 'system'},
                {'id': 'export_course_document', 'provider': 'system'}
            ],
            system_prompt=system_prompt,
            handoffs=handoffs
        )
```

---

#### 🔧 工具定义

**你们需要的工具**:

```python
# 1. 项目基础定义工具
async def define_project_foundation(
    student_needs: str,
    project_topic: str,
    learning_objectives: List[str],
    **kwargs
) -> str:
    """
    定义项目基础

    保存到画布:
    - 项目主题卡片
    - 核心问题卡片
    - 学习目标列表
    """
    canvas_id = kwargs.get('canvas_id')
    session_id = kwargs.get('session_id')

    # 生成结构化数据
    foundation = {
        'project_topic': project_topic,
        'core_question': extract_core_question(student_needs),
        'learning_objectives': learning_objectives
    }

    # 推送到画布
    await send_to_websocket(session_id, {
        'type': 'add_foundation_cards',
        'data': foundation
    })

    return "项目基础定义完成"

# 2. 评估框架设计工具
async def design_assessment_framework(
    assessment_criteria: List[str],
    rubric: Dict[str, Any],
    timeline: List[Dict[str, str]],
    **kwargs
) -> str:
    """
    设计评估框架

    保存到画布:
    - 评估标准卡片
    - 评估量规表格
    - 评估时间线
    """
    session_id = kwargs.get('session_id')

    framework = {
        'criteria': assessment_criteria,
        'rubric': rubric,
        'timeline': timeline
    }

    await send_to_websocket(session_id, {
        'type': 'add_assessment_framework',
        'data': framework
    })

    return "评估框架设计完成"

# 3. 学习蓝图生成工具
async def generate_learning_blueprint(
    activities: List[Dict[str, Any]],
    resources: List[str],
    **kwargs
) -> str:
    """
    生成学习蓝图

    保存到画布:
    - 活动时间线
    - 活动详情卡片
    - 资源清单
    """
    session_id = kwargs.get('session_id')

    blueprint = {
        'activities': activities,
        'resources': resources
    }

    await send_to_websocket(session_id, {
        'type': 'add_learning_blueprint',
        'data': blueprint
    })

    return "学习蓝图生成完成"

# 4. 文档导出工具
async def export_course_document(
    format: str = 'markdown',
    **kwargs
) -> str:
    """
    导出课程文档

    支持格式:
    - markdown
    - pdf
    - word
    """
    canvas_id = kwargs.get('canvas_id')
    session_id = kwargs.get('session_id')

    # 从画布获取所有数据
    canvas_data = await get_canvas_data(canvas_id)

    # 生成文档
    document = generate_document(canvas_data, format)

    # 推送下载链接
    await send_to_websocket(session_id, {
        'type': 'document_ready',
        'download_url': document.url
    })

    return f"文档导出完成: {document.url}"
```

---

#### 🔧 前端画布（tldraw 替换 Excalidraw）

**tldraw 集成**: `frontend-v2/src/components/canvas/CanvasTldraw.tsx`

```typescript
import { Tldraw, Editor, TLShape } from 'tldraw'
import { useEffect, useState } from 'react'
import { useCanvas } from '@/contexts/canvas'
import { eventBus } from '@/lib/event'

const CanvasTldraw = ({ canvasId, initialData }) => {
  const [editor, setEditor] = useState<Editor | null>(null)

  useEffect(() => {
    if (!editor) return

    // 监听添加项目基础卡片事件
    const handleAddFoundation = (data: any) => {
      // 创建项目主题卡片
      const topicCard: TLShape = {
        id: `topic-${Date.now()}`,
        type: 'geo',
        x: 100,
        y: 100,
        props: {
          w: 300,
          h: 150,
          text: `📌 项目主题\n${data.project_topic}`,
          color: 'blue',
          fill: 'solid'
        }
      }

      // 创建核心问题卡片
      const questionCard: TLShape = {
        id: `question-${Date.now()}`,
        type: 'geo',
        x: 100,
        y: 300,
        props: {
          w: 300,
          h: 150,
          text: `❓ 核心问题\n${data.core_question}`,
          color: 'orange',
          fill: 'solid'
        }
      }

      // 创建学习目标列表
      const objectivesCards = data.learning_objectives.map((obj, idx) => ({
        id: `objective-${idx}-${Date.now()}`,
        type: 'geo',
        x: 450,
        y: 100 + idx * 180,
        props: {
          w: 250,
          h: 120,
          text: `🎯 目标 ${idx + 1}\n${obj}`,
          color: 'green',
          fill: 'semi'
        }
      }))

      // 添加到画布
      editor.createShapes([topicCard, questionCard, ...objectivesCards])
    }

    // 监听添加评估框架事件
    const handleAddAssessment = (data: any) => {
      // 创建评估标准卡片
      const criteriaCards = data.criteria.map((criterion, idx) => ({
        id: `criterion-${idx}-${Date.now()}`,
        type: 'geo',
        x: 100,
        y: 500 + idx * 150,
        props: {
          w: 300,
          h: 100,
          text: `📊 评估标准 ${idx + 1}\n${criterion}`,
          color: 'red',
          fill: 'pattern'
        }
      }))

      // 创建评估量规表格（使用 frame）
      const rubricFrame = {
        id: `rubric-${Date.now()}`,
        type: 'frame',
        x: 450,
        y: 500,
        props: {
          w: 600,
          h: 400,
          name: '评估量规'
        }
      }

      editor.createShapes([...criteriaCards, rubricFrame])
    }

    // 监听添加学习蓝图事件
    const handleAddBlueprint = (data: any) => {
      // 创建活动时间线
      const activityCards = data.activities.map((activity, idx) => ({
        id: `activity-${idx}-${Date.now()}`,
        type: 'geo',
        x: 100 + idx * 250,
        y: 1000,
        props: {
          w: 220,
          h: 180,
          text: `📅 第${idx + 1}周\n${activity.title}\n⏱️ ${activity.duration}`,
          color: 'violet',
          fill: 'solid'
        }
      }))

      // 添加连接箭头
      const arrows = activityCards.slice(0, -1).map((card, idx) => ({
        id: `arrow-${idx}-${Date.now()}`,
        type: 'arrow',
        props: {
          start: { x: card.x + 220, y: card.y + 90 },
          end: { x: activityCards[idx + 1].x, y: activityCards[idx + 1].y + 90 }
        }
      }))

      editor.createShapes([...activityCards, ...arrows])
    }

    eventBus.on('add_foundation_cards', handleAddFoundation)
    eventBus.on('add_assessment_framework', handleAddAssessment)
    eventBus.on('add_learning_blueprint', handleAddBlueprint)

    return () => {
      eventBus.off('add_foundation_cards', handleAddFoundation)
      eventBus.off('add_assessment_framework', handleAddAssessment)
      eventBus.off('add_learning_blueprint', handleAddBlueprint)
    }
  }, [editor])

  return (
    <Tldraw
      onMount={(editor) => {
        setEditor(editor)

        // 加载初始数据
        if (initialData) {
          editor.store.loadSnapshot(initialData)
        }
      }}
      onUiEvent={(name, data) => {
        // 监听 UI 事件
        console.log('tldraw event:', name, data)
      }}
    />
  )
}

export default CanvasTldraw
```

---

## 实施路线图

### Phase 1: 后端 Agent 系统搭建 (2-3天)

**目标**: 完成三 Agent 工作流，支持流式响应

**任务清单**:

1. ✅ **复制 Jaaz LangGraph 模块**
   ```bash
   cp -r jaaz/server/services/langgraph_service backend/app/services/
   cp jaaz/server/services/chat_service.py backend/app/services/
   cp jaaz/server/services/websocket_service.py backend/app/services/
   ```

2. ✅ **修改 Agent 配置**
   - `configs/project_foundation_config.py` (新建)
   - `configs/assessment_framework_config.py` (新建)
   - `configs/learning_blueprint_config.py` (新建)
   - 删除 `configs/image_vide_creator_config.py`

3. ✅ **定义工具函数**
   ```bash
   mkdir backend/app/tools
   touch backend/app/tools/project_foundation.py
   touch backend/app/tools/assessment_framework.py
   touch backend/app/tools/learning_blueprint.py
   touch backend/app/tools/document_export.py
   ```

4. ✅ **注册工具到 tool_service**
   ```python
   # backend/app/services/tool_service.py
   from tools.project_foundation import define_project_foundation_tool
   from tools.assessment_framework import design_assessment_framework_tool
   from tools.learning_blueprint import generate_learning_blueprint_tool
   from tools.document_export import export_course_document_tool

   tool_service.register_tool('define_project_foundation', define_project_foundation_tool)
   tool_service.register_tool('design_assessment_framework', design_assessment_framework_tool)
   tool_service.register_tool('generate_learning_blueprint', generate_learning_blueprint_tool)
   tool_service.register_tool('export_course_document', export_course_document_tool)
   ```

5. ✅ **测试 Agent 切换流程**
   ```python
   # backend/test_agent_flow.py
   import asyncio
   from app.services.langgraph_service.agent_service import langgraph_multi_agent

   async def test_flow():
       messages = [{'role': 'user', 'content': '为高中生设计一个环保主题的 PBL 项目'}]
       await langgraph_multi_agent(
           messages=messages,
           canvas_id='test-canvas',
           session_id='test-session',
           text_model={'model': 'gpt-4o', 'provider': 'openai'},
           tool_list=[]
       )

   asyncio.run(test_flow())
   ```

---

### Phase 2: 前端画布与 WebSocket 集成 (2-3天)

**目标**: tldraw 画布 + 实时同步

**任务清单**:

1. ✅ **安装依赖**
   ```bash
   cd frontend-v2
   npm install tldraw socket.io-client mitt
   ```

2. ✅ **复制 Jaaz WebSocket 模块**
   ```bash
   cp -r jaaz/react/src/contexts/socket.tsx frontend-v2/src/contexts/
   cp -r jaaz/react/src/lib/socket.ts frontend-v2/src/lib/
   cp -r jaaz/react/src/lib/event.ts frontend-v2/src/lib/
   ```

3. ✅ **创建 tldraw 画布组件**
   ```bash
   touch frontend-v2/src/components/canvas/CanvasTldraw.tsx
   ```

4. ✅ **修改主页面布局**
   ```typescript
   // frontend-v2/src/pages/CourseDesignPage.tsx
   import CanvasTldraw from '@/components/canvas/CanvasTldraw'
   import ChatInterface from '@/components/chat/ChatInterface'

   <ResizablePanelGroup direction="horizontal">
     <ResizablePanel defaultSize={75}>
       <CanvasTldraw canvasId={canvasId} />
     </ResizablePanel>

     <ResizableHandle />

     <ResizablePanel defaultSize={25}>
       <ChatInterface canvasId={canvasId} />
     </ResizablePanel>
   </ResizablePanelGroup>
   ```

5. ✅ **实现 WebSocket 事件监听**
   ```typescript
   // frontend-v2/src/components/chat/ChatInterface.tsx
   useEffect(() => {
     socketManager.on('add_foundation_cards', (data) => {
       eventBus.emit('add_foundation_cards', data)
     })

     socketManager.on('add_assessment_framework', (data) => {
       eventBus.emit('add_assessment_framework', data)
     })

     socketManager.on('add_learning_blueprint', (data) => {
       eventBus.emit('add_learning_blueprint', data)
     })
   }, [socketManager])
   ```

---

### Phase 3: 联调与优化 (1-2天)

**目标**: 完整流程跑通，体验优化

**任务清单**:

1. ✅ **端到端测试**
   - 用户输入 → Agent 工作流 → 画布更新
   - 检查每个 Agent 的输出是否正确
   - 检查画布元素是否正确添加

2. ✅ **错误处理**
   - Agent 执行失败重试
   - WebSocket 断线重连
   - 工具调用超时处理

3. ✅ **性能优化**
   - 画布元素批量添加
   - WebSocket 消息去重
   - 数据库查询优化

4. ✅ **UI 优化**
   - 加载状态显示
   - 进度条展示
   - 错误提示友好化

---

## 总结

### 核心收获

1. **Jaaz 的架构与你们 Phase 2 高度契合**（相似度 > 90%）
2. **LangGraph Swarm 是多 Agent 编排的最佳实践**
3. **WebSocket + 流式响应 + 画布同步是标准模式**
4. **Excalidraw 和 tldraw 的 API 不同，但逻辑相似**

### 关键技术点

1. **Agent 切换**: 通过特殊的 `transfer_to_{agent_name}` 工具实现
2. **流式推送**: LangGraph 的 `astream` + StreamProcessor
3. **画布同步**: WebSocket 事件 → EventBus → 画布 API
4. **工具调用**: LangChain StructuredTool + 上下文传递

### 建议的下一步

1. **立即开始 Phase 1**: 复制 LangGraph 模块，修改 Agent 配置
2. **并行进行 Phase 2**: 前端同学开始 tldraw 集成
3. **预留 1 周时间**: 用于联调和优化

---

**最终评估**: Jaaz 项目为你们提供了一个**几乎完美的参考模板**，80% 的代码可以直接复用或微调后使用。建议尽快启动实施，预计 1 周内可以完成 MVP。

---

**文档版本**: v1.0
**最后更新**: 2025-10-05
**作者**: Claude Code (Linus Mode)
