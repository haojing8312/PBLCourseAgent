# Project Genesis AI - 第二阶段技术实现方案

**文档版本:** 1.0
**创建日期:** 2025-09-29
**基于:** PRD v2.1 - The Conversational Canvas

---

## 1. 架构转型分析

### 1.1 核心变化
- **交互模式**: 从"表单式单次生成"转为"对话式持续创作"
- **输出格式**: 从"JSON输出"转为"富文本展示+文档导出"
- **技术架构**: 从"纯后端逻辑"转为"前后端实时协同"

### 1.2 技术挑战
- 流式生成与实时UI更新的性能优化
- 复杂状态管理与前后端同步
- 中文文档导出的兼容性问题
- 单容器部署的便捷性要求

---

## 2. 对话式画布技术架构

### 2.1 前端架构重构

```
frontend/
├── src/
│   ├── components/
│   │   ├── ConversationCanvas/     # 核心对话画布组件
│   │   │   ├── ChatPanel.tsx       # 左侧对话区
│   │   │   ├── CourseCanvas.tsx    # 右侧课程画布
│   │   │   ├── StreamRenderer.tsx  # 流式内容渲染器
│   │   │   └── CanvasSection.tsx   # 画布可点击模块
│   │   ├── DocumentExport/         # 文档导出组件
│   │   └── SessionManager/         # 会话管理
│   ├── services/
│   │   ├── streamingService.ts     # 流式数据处理
│   │   ├── sessionService.ts       # 本地会话存储
│   │   └── exportService.ts        # 导出服务
│   ├── stores/                     # 状态管理
│   │   ├── conversationStore.ts    # 对话状态
│   │   ├── canvasStore.ts         # 画布内容状态
│   │   └── sessionStore.ts        # 会话状态
│   └── types/
│       ├── conversation.ts         # 对话相关类型
│       └── canvas.ts              # 画布相关类型
```

### 2.2 技术选型

| 技术栈 | 选择 | 理由 |
|--------|------|------|
| 前端框架 | React 18 + TypeScript + Vite | 成熟生态，类型安全，快速构建 |
| 状态管理 | Zustand | 轻量级，适合实时状态同步 |
| 流式通信 | SSE (Server-Sent Events) | 简单可靠，浏览器原生支持 |
| 富文本渲染 | React Markdown + 自定义组件 | 灵活的Markdown渲染和扩展 |
| 本地存储 | localStorage + sessionStorage | 支持会话恢复，无需后端存储 |

### 2.3 核心功能实现

#### 双栏布局设计
```tsx
// ConversationCanvas.tsx
interface ConversationCanvasProps {
  sessionId: string;
}

const ConversationCanvas: React.FC<ConversationCanvasProps> = ({ sessionId }) => {
  return (
    <div className="flex h-screen">
      <ChatPanel className="w-1/2" onMessage={handleMessage} />
      <CourseCanvas className="w-1/2" content={canvasContent} />
    </div>
  );
};
```

#### 会话管理
```typescript
// sessionService.ts
interface Session {
  id: string;
  title: string;
  conversation: Message[];
  canvasContent: CanvasContent;
  createdAt: Date;
  updatedAt: Date;
}

class SessionService {
  createNewSession(): Session;
  saveSession(session: Session): void;
  loadSession(id: string): Session | null;
  restoreLastSession(): Session | null;
}
```

---

## 3. 流式生成与实时同步方案

### 3.1 后端流式API设计

```python
# 新增路由
@router.post("/conversation/stream")
async def stream_conversation(message: ConversationMessage):
    """流式对话接口，支持实时内容生成"""
    return StreamingResponse(
        stream_conversation_response(message),
        media_type="text/event-stream"
    )

# 核心流式生成服务
class StreamingService:
    async def stream_response(self, message: str, context: dict):
        """生成流式响应，同时更新画布内容"""
        async for chunk in openai_client.stream_chat(message, context):
            # 解析chunk中的结构化内容
            canvas_update = self.parse_canvas_update(chunk)
            yield {
                "type": "chat_chunk",
                "content": chunk,
                "canvas_update": canvas_update,
                "timestamp": time.time()
            }
```

### 3.2 前端流式处理

```typescript
// streamingService.ts
class StreamingService {
  private eventSource: EventSource | null = null;

  async startStream(message: string, onChunk: (chunk: StreamChunk) => void) {
    this.eventSource = new EventSource(`/api/v1/conversation/stream`);

    this.eventSource.onmessage = (event) => {
      const chunk = JSON.parse(event.data);
      onChunk(chunk);
    };

    this.eventSource.onerror = () => {
      this.handleReconnect();
    };
  }

  private handleReconnect() {
    // 自动重连逻辑
  }
}
```

### 3.3 性能优化策略

#### 首字符响应优化
- **预处理**: AI模型预热，减少冷启动时间
- **缓存策略**: 常用上下文和模板缓存
- **连接复用**: 保持长连接，避免重复握手

#### 渲染性能优化
```typescript
// StreamRenderer.tsx
const StreamRenderer: React.FC = () => {
  const [content, setContent] = useState('');

  // 使用节流避免过度渲染
  const throttledUpdate = useCallback(
    throttle((newContent: string) => {
      setContent(newContent);
    }, 50),
    []
  );

  // 虚拟滚动处理大量内容
  const virtualizedContent = useMemo(() => {
    return processLargeContent(content);
  }, [content]);

  return <VirtualizedMarkdown content={virtualizedContent} />;
};
```

---

## 4. 教学资源生成扩展架构

### 4.1 Agent角色转换机制

```python
class ConversationMode(Enum):
    COURSE_DESIGN = "course_design"      # 课程设计模式
    RESOURCE_CREATION = "resource_creation"  # 资源创建模式

class ResourceGenerationAgent:
    """教学资源生成Agent，接续核心课程设计"""

    SUPPORTED_RESOURCES = [
        "opening_speech",      # 开场白
        "student_handout",     # 学生指引
        "activity_guide",      # 活动指南
        "assessment_sheet",    # 评估表单
        "interactive_games",   # 互动游戏
        "presentation_slides", # 演示文稿大纲
    ]

    async def generate_resource(self,
                              request: str,
                              course_context: dict,
                              resource_type: str) -> dict:
        """根据课程上下文生成具体教学资源"""

        # 1. 验证资源类型
        if resource_type not in self.SUPPORTED_RESOURCES:
            raise ValueError(f"不支持的资源类型: {resource_type}")

        # 2. 构建资源生成Prompt
        resource_prompt = self.build_resource_prompt(
            request, course_context, resource_type
        )

        # 3. 流式生成资源内容
        async for chunk in self.stream_generate(resource_prompt):
            yield {
                "type": "resource_chunk",
                "resource_type": resource_type,
                "content": chunk,
                "canvas_section": "teaching_resources"
            }
```

### 4.2 上下文延续策略

```python
class ContextManager:
    """上下文管理器，确保资源生成与课程设计的连贯性"""

    def __init__(self):
        self.course_context = {}
        self.conversation_history = []

    def update_course_context(self, agent_output: dict):
        """更新课程上下文"""
        self.course_context.update({
            "project_foundation": agent_output.get("project_foundation"),
            "assessment_framework": agent_output.get("assessment_framework"),
            "learning_blueprint": agent_output.get("learning_blueprint"),
            "course_metadata": agent_output.get("metadata")
        })

    def get_resource_context(self, resource_type: str) -> dict:
        """获取特定资源类型所需的上下文"""
        context_mapping = {
            "opening_speech": ["project_foundation", "course_metadata"],
            "student_handout": ["learning_blueprint", "assessment_framework"],
            "interactive_games": ["learning_blueprint", "project_foundation"],
            # ... 其他映射
        }

        required_keys = context_mapping.get(resource_type, [])
        return {key: self.course_context[key] for key in required_keys}
```

### 4.3 资源模板系统

```python
class ResourceTemplateManager:
    """资源模板管理器"""

    TEMPLATES = {
        "opening_speech": """
        基于以下课程信息，生成一段{duration}的开场白：

        课程主题：{course_topic}
        驱动性问题：{driving_question}
        目标年龄：{age_group}

        要求：
        1. 激发学生兴趣和好奇心
        2. 简洁明了，符合年龄特点
        3. 引出驱动性问题
        """,

        "student_handout": """
        为 "{activity_name}" 活动创建学生操作指南：

        活动目标：{activity_objectives}
        所需工具：{required_tools}
        时长：{duration}

        格式要求：
        1. A4页面，清晰排版
        2. 分步骤说明
        3. 包含检查清单
        """,
        # ... 其他模板
    }

    def get_template(self, resource_type: str, context: dict) -> str:
        template = self.TEMPLATES.get(resource_type, "")
        return template.format(**context)
```

---

## 5. 文档导出技术方案

### 5.1 导出服务架构

```python
from docx import Document
from weasyprint import HTML, CSS
import io
from typing import Union

class DocumentExportService:
    """专业级文档导出服务"""

    def __init__(self):
        self.font_manager = ChineseFontManager()

    async def export_to_docx(self, canvas_content: dict) -> bytes:
        """导出Word文档，解决中文字体问题"""
        doc = Document()

        # 设置中文字体
        self.font_manager.setup_docx_fonts(doc)

        # 渲染内容
        self.render_canvas_to_docx(doc, canvas_content)

        # 返回字节流
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    async def export_to_pdf(self, canvas_content: dict) -> bytes:
        """导出PDF文档，确保矢量格式"""
        # 将canvas内容转换为HTML
        html_content = self.render_canvas_to_html(canvas_content)

        # CSS样式，包含中文字体
        css_styles = self.font_manager.get_pdf_css()

        # 生成PDF
        pdf_bytes = HTML(string=html_content).write_pdf(
            stylesheets=[CSS(string=css_styles)]
        )

        return pdf_bytes
```

### 5.2 中文字体支持方案

```python
class ChineseFontManager:
    """中文字体管理器"""

    def __init__(self):
        # 使用开源字体避免版权问题
        self.chinese_fonts = [
            "Noto Sans CJK SC",  # 思源黑体
            "Noto Serif CJK SC", # 思源宋体
            "SimHei",            # 黑体（系统备选）
            "SimSun",            # 宋体（系统备选）
        ]

    def setup_docx_fonts(self, doc: Document):
        """设置Word文档中文字体"""
        # 设置默认字体
        style = doc.styles['Normal']
        font = style.font
        font.name = self.chinese_fonts[0]
        font.size = Pt(12)

        # 设置标题字体
        for level in range(1, 4):
            heading_style = doc.styles[f'Heading {level}']
            heading_font = heading_style.font
            heading_font.name = self.chinese_fonts[0]

    def get_pdf_css(self) -> str:
        """获取PDF导出的CSS样式"""
        font_family = ", ".join([f'"{font}"' for font in self.chinese_fonts])

        return f"""
        @page {{
            size: A4;
            margin: 2cm;
        }}

        body {{
            font-family: {font_family};
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: {font_family};
            color: #2c5aa0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        """
```

### 5.3 富文本格式映射

```python
class ContentRenderer:
    """内容渲染器，处理Markdown到Word/PDF的转换"""

    def render_canvas_to_docx(self, doc: Document, canvas_content: dict):
        """将画布内容渲染为Word文档"""

        # 渲染封面
        if "cover_page" in canvas_content:
            self.add_cover_page(doc, canvas_content["cover_page"])

        # 渲染各个章节
        sections = [
            ("project_foundation", "项目基础定义"),
            ("assessment_framework", "评估框架"),
            ("learning_blueprint", "学习蓝图"),
            ("teaching_resources", "教学资源")
        ]

        for section_key, section_title in sections:
            if section_key in canvas_content:
                self.add_section(doc, section_title, canvas_content[section_key])

    def add_rubric_table(self, doc: Document, rubric_data: list):
        """添加评估量规表格"""
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'

        # 表头
        header_cells = table.rows[0].cells
        headers = ['评估维度', '优秀', '良好', '需改进']
        for i, header in enumerate(headers):
            header_cells[i].text = header
            header_cells[i].paragraphs[0].runs[0].bold = True

        # 表格内容
        for rubric in rubric_data:
            row_cells = table.add_row().cells
            row_cells[0].text = rubric.get('dimension', '')
            row_cells[1].text = rubric.get('excellent', '')
            row_cells[2].text = rubric.get('good', '')
            row_cells[3].text = rubric.get('needs_improvement', '')
```

---

## 6. Docker容器化部署方案

### 6.1 多阶段构建Dockerfile

```dockerfile
# 前端构建阶段
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制package文件并安装依赖
COPY frontend/package*.json ./
RUN npm ci --only=production

# 复制源代码并构建
COPY frontend/ ./
RUN npm run build

# 后端运行阶段
FROM python:3.10-slim AS backend

WORKDIR /app

# 安装系统依赖（PDF/Word导出需要）
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖并安装
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建导出目录
RUN mkdir -p /app/exports

# 设置环境变量
ENV PYTHONPATH=/app
ENV STATIC_FILES_DIR=/app/static

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  eduagents:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: project-genesis-ai
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o}
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:8000}
    volumes:
      - ./exports:/app/exports
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - eduagents-network

networks:
  eduagents-network:
    driver: bridge

# 开发环境配置
# docker-compose.dev.yml
version: '3.8'

services:
  eduagents-dev:
    extends:
      file: docker-compose.yml
      service: eduagents
    volumes:
      - ./backend:/app
      - ./frontend/dist:/app/static
      - ./exports:/app/exports
      - ./logs:/app/logs
    environment:
      - DEBUG=true
      - RELOAD=true
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 6.3 部署脚本与文档

```bash
#!/bin/bash
# deploy.sh - 一键部署脚本

set -e

echo "🚀 Project Genesis AI 部署脚本"
echo "================================"

# 检查Docker环境
if ! command -v docker &> /dev/null; then
    echo "❌ 请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 请先安装Docker Compose"
    exit 1
fi

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ 请设置OPENAI_API_KEY环境变量"
    echo "   示例: export OPENAI_API_KEY=your_api_key"
    exit 1
fi

# 创建必要目录
mkdir -p exports logs

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 健康检查
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ 部署成功!"
    echo "🌐 访问地址: http://localhost:8000"
    echo "📖 API文档: http://localhost:8000/docs"
else
    echo "❌ 服务启动失败，请检查日志:"
    docker-compose logs
    exit 1
fi
```

### 6.4 优化策略

#### 镜像大小优化
- 使用多阶段构建，只保留运行时必需的文件
- 清理apt缓存和临时文件
- 使用.dockerignore排除不需要的文件

#### 安全配置
```dockerfile
# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser
```

#### 性能优化
- 预装中文字体，避免运行时下载
- 使用pip缓存加速依赖安装
- 配置适当的健康检查间隔

---

## 7. 开发实施计划

### 7.1 阶段划分

#### Phase 1: 核心架构搭建 (2-3周)
- [ ] React前端重构，实现双栏布局
- [ ] 状态管理架构设计与实现
- [ ] 基础SSE流式通信建立
- [ ] 简单的Markdown渲染实现

#### Phase 2: 交互体验优化 (2-3周)
- [ ] 流式渲染性能优化
- [ ] 画布模块点击交互
- [ ] 会话管理与本地存储
- [ ] 错误处理与重连机制

#### Phase 3: 功能扩展 (2-3周)
- [ ] 教学资源生成Agent实现
- [ ] 上下文管理优化
- [ ] 资源模板系统开发
- [ ] 资源类型扩展

#### Phase 4: 文档导出 (2-3周)
- [ ] Word导出功能实现
- [ ] PDF导出功能实现
- [ ] 中文字体兼容性测试
- [ ] 导出格式优化

#### Phase 5: 部署优化 (1-2周)
- [ ] Docker容器化实现
- [ ] 部署脚本编写
- [ ] 文档完善
- [ ] 性能测试与优化

### 7.2 关键里程碑

| 里程碑 | 目标 | 验收标准 |
|--------|------|----------|
| M1 | 基础对话界面 | 双栏布局，基本对话功能 |
| M2 | 流式内容展示 | <1.5s首字符响应，流畅渲染 |
| M3 | 完整课程生成 | 三大模块完整生成并展示 |
| M4 | 资源生成扩展 | 至少支持3种教学资源类型 |
| M5 | 文档导出就绪 | Word/PDF导出，中文字体正常 |
| M6 | 部署就绪 | 一键Docker部署，文档完善 |

### 7.3 风险评估与缓解策略

#### 高风险项
1. **流式渲染性能**
   - 风险：大量内容导致UI卡顿
   - 缓解：虚拟滚动，内容分块，性能监控

2. **中文PDF导出兼容性**
   - 风险：不同系统字体显示异常
   - 缓解：内置字体，多环境测试，降级方案

#### 中风险项
1. **前端状态同步复杂度**
   - 风险：状态管理逻辑复杂，易出错
   - 缓解：详细测试，状态图建模，渐进式开发

2. **Docker镜像大小**
   - 风险：镜像过大，部署缓慢
   - 缓解：多阶段构建，依赖优化，镜像分层

---

## 8. 技术选型总结

| 类别 | 选择 | 替代方案 | 选择理由 |
|------|------|----------|----------|
| 前端框架 | React 18 + TypeScript | Vue.js, Svelte | 生态成熟，团队熟悉 |
| 状态管理 | Zustand | Redux, Recoil | 轻量级，学习成本低 |
| 流式通信 | SSE | WebSocket | 简单可靠，单向通信足够 |
| 构建工具 | Vite | Webpack, Parcel | 开发体验好，构建速度快 |
| 富文本渲染 | React Markdown | 自研组件 | 功能完备，社区支持好 |
| Word导出 | python-docx | 其他库 | Python生态最佳选择 |
| PDF导出 | WeasyPrint | ReportLab | HTML/CSS支持好，中文友好 |
| 容器化 | Docker | 其他方案 | 标准化，跨平台兼容 |

---

## 9. 后续优化方向

### 9.1 性能优化
- CDN集成，加速资源加载
- Service Worker，离线支持
- 预渲染优化，SEO友好

### 9.2 功能扩展
- 多语言支持（i18n）
- 自定义主题系统
- 插件化架构

### 9.3 开发体验
- Storybook组件文档
- E2E测试覆盖
- CI/CD流水线

---

**文档维护者:** Claude Code
**最后更新:** 2025-09-29
**审核状态:** 待审核