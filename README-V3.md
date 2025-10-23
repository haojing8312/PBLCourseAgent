# UbD-PBL 课程架构师 V3

> **AI驱动的专业课程设计工具** - 基于Understanding by Design (UbD)框架，帮助教师创建高质量的项目式学习(PBL)课程方案

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

---

## ✨ 核心特性

### 🎯 UbD三阶段设计

遵循逆向设计理念，以终为始：

1. **确定预期学习结果** (G/U/Q/K/S)
2. **确定可接受的证据** (驱动性问题 + 表现性任务)
3. **规划学习体验** (PBL四阶段 + WHERETO原则)

### 🤖 AI智能生成

- **三Agent系统**: ProjectFoundation → AssessmentFramework → LearningBlueprint
- **SSE流式生成**: 实时显示生成进度
- **语义质量验证**: 自动检测"持续理解(U)"的质量，提供改进建议
- **PHR版本控制**: Prompt History Records，可追溯的提示词版本管理

### 💬 ChatGPT式交互

- **Ant Design X对话界面**: 类似ChatGPT的流畅体验
- **上下文对话**: AI理解课程设计意图，提供专业建议
- **对话历史**: 自动保存对话记录，随时回溯

### 📚 理论学习

- **内置帮助文档**: 完整的UbD框架说明
- **新手引导**: 5步教程介绍核心概念
- **质量指示器**: 实时显示生成内容的质量分数
- **UbD Tooltips**: 鼠标悬停即可查看G/U/Q/K/S定义

### 📝 编辑与导出

- **双模式编辑器**: 查看/编辑模式随时切换
- **自动保存**: 1秒防抖，避免丢失修改
- **Markdown导出**: 下载完整的、结构化的教案文档
- **变更检测**: 修改Stage 1后，提示重新生成Stage 2/3（保持一致性）

---

## 🏗️ 技术架构

### 后端技术栈

```
FastAPI 0.100+        # Web框架
SQLAlchemy 2.0+       # ORM
SQLite                # 数据库 (MVP)
OpenAI API            # LLM接口
Pydantic 2.0+         # 数据验证
Jinja2                # 模板引擎
sentence-transformers # 语义相似度
```

### 前端技术栈

```
React 18              # UI框架
TypeScript 4.9+       # 类型安全
Ant Design 5.0+       # UI组件库
Ant Design X          # AI对话组件
Zustand               # 状态管理
react-markdown        # Markdown渲染
Vite                  # 构建工具
```

### 架构亮点

- **SSE流式生成**: Server-Sent Events实时推送
- **三Agent流水线**: 顺序依赖的Agent执行
- **状态持久化**: Zustand + localStorage
- **语义验证**: sentence-transformers模型检测U vs K
- **模板导出**: Jinja2渲染UbD教案

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- OpenAI API Key (或兼容的LLM API)

### 后端启动

```bash
cd backend

# 安装依赖 (使用uv包管理器)
uv sync

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥

# 启动服务
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 48097
```

### 前端启动

```bash
cd frontend-x

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:48098
```

### Docker部署 (可选)

```bash
docker-compose up -d
```

---

## 📖 用户指南

详见 [docs/user-guide-v3.md](docs/user-guide-v3.md)

### 基本流程

1. **创建课程** → 填写课程名称、学科、时长等信息
2. **AI生成** → 自动生成UbD三阶段内容 (约60-90秒)
3. **对话完善** → 左侧ChatPanel与AI交流
4. **查看编辑** → 右侧ContentPanel查看结构化内容
5. **导出教案** → 下载Markdown格式的完整教案

### 质量指示器

- 🟢 **优秀 (≥85%)**: 抽象的big idea，符合U的定义
- 🟡 **合格 (70-84%)**: 基本符合要求
- 🟠 **需改进 (<70%)**: 可能过于具体，建议修改

---

## 📁 项目结构

```
eduagents/
├── backend/                 # Python FastAPI后端
│   ├── app/
│   │   ├── agents/          # 三个AI Agent (V3版本)
│   │   │   ├── project_foundation_v3.py
│   │   │   ├── assessment_framework_v3.py
│   │   │   └── learning_blueprint_v3.py
│   │   ├── api/v1/          # API端点
│   │   │   ├── course.py    # 课程CRUD
│   │   │   └── generate.py  # SSE流式生成
│   │   ├── models/          # SQLAlchemy模型
│   │   │   ├── course_project.py
│   │   │   └── stage_data.py
│   │   ├── services/        # 业务逻辑
│   │   │   ├── workflow_service_v3.py
│   │   │   ├── validation_service.py
│   │   │   └── export_service.py
│   │   ├── prompts/phr/     # Prompt History Records
│   │   │   ├── project_foundation_v2.md
│   │   │   ├── assessment_framework_v2.md
│   │   │   └── learning_blueprint_v2.md
│   │   └── templates/       # Jinja2模板
│   │       └── course_export_v3.md.jinja2
│   ├── tests/               # 测试套件
│   └── pyproject.toml       # uv项目配置
│
├── frontend-x/              # React + TypeScript前端
│   ├── src/
│   │   ├── components/      # React组件
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── ContentPanel.tsx
│   │   │   ├── MarkdownEditor.tsx
│   │   │   ├── HelpDialog.tsx
│   │   │   ├── OnboardingOverlay.tsx
│   │   │   ├── ProjectListView.tsx
│   │   │   ├── ChangeDetectionDialog.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── hooks/           # Custom Hooks
│   │   │   ├── useStepWorkflow.ts
│   │   │   ├── useChatConversation.ts
│   │   │   └── useMarkdownSync.ts
│   │   ├── services/        # API调用
│   │   │   ├── workflowService.ts
│   │   │   ├── conversationService.ts
│   │   │   └── exportService.ts
│   │   ├── stores/          # Zustand Store
│   │   │   └── courseStore.ts
│   │   ├── types/           # TypeScript类型
│   │   │   └── course.ts
│   │   └── constants/       # 常量
│   │       └── ubdDefinitions.ts
│   └── package.json
│
├── docs/                    # 文档
│   ├── user-guide-v3.md     # 用户指南
│   ├── UBD教案模板.md
│   └── ubd教案案例一.md
│
└── specs/                   # 规格文档
    └── 001-ubd-pbl-architect-v3/
        ├── spec.md          # 功能规格
        ├── plan.md          # 实施计划
        └── tasks.md         # 任务清单
```

---

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest app/tests/test_agents/ -v

# 运行语义验证测试
uv run pytest app/tests/test_validation_service.py -v
```

### 前端测试

```bash
cd frontend-x

# 运行单元测试
npm run test

# 运行E2E测试
npm run test:e2e
```

---

## 📊 开发进度

### ✅ Phase 1-3: MVP核心功能 (已完成)

- [x] PHR v2 Prompt管理
- [x] 三Agent V3实现
- [x] SSE流式生成
- [x] 语义质量验证
- [x] ChatGPT式UI
- [x] Markdown导出
- [x] 对话历史持久化

### ✅ Phase 4: UbD理论学习 (已完成)

- [x] HelpDialog完整帮助文档
- [x] OnboardingOverlay新手引导
- [x] 验证质量指示器
- [x] WHERETO标签tooltip

### 🚧 Phase 5-6: 高级功能 (部分完成)

- [x] ChangeDetectionDialog变更检测
- [x] ProjectListView项目管理
- [ ] 级联重生成集成
- [ ] 项目列表导航

### 🚧 Phase 7: Polish (部分完成)

- [x] ErrorBoundary错误边界
- [x] 用户指南文档
- [ ] 性能优化 (lazy loading)
- [ ] 完整测试套件
- [ ] Docker部署

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

### Commit Message规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
test: 测试相关
refactor: 代码重构
perf: 性能优化
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- **Understanding by Design**: Grant Wiggins & Jay McTighe
- **Ant Design Team**: UI组件库
- **OpenAI**: GPT-4o API
- **FastAPI**: Sebastián Ramírez

---

## 📮 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/yourusername/eduagents/issues)
- **功能建议**: [GitHub Discussions](https://github.com/yourusername/eduagents/discussions)

---

*UbD-PBL课程架构师V3 - 让优秀的课程设计触手可及* 🎓
