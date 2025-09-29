# 🤖 PBLCourseAgent

> AI-Powered PBL Course Designer with Visual Task-Driven Canvas
> 基于AI的项目式学习课程设计助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

PBLCourseAgent 是一个创新的AI驱动的项目式学习(PBL)课程设计工具。它采用现代AI Agent产品的设计理念，通过**无限画布 + 任务节点 + AI对话**的方式，让教育者能够轻松创建高质量的PBL课程方案。

## ✨ 核心特性

- 🎨 **无限画布设计**: 基于tldraw的专业级无限画布，支持复杂工作流可视化
- 🤖 **AI智能助手**: 集成OpenAI GPT-4，提供专业的PBL课程设计建议
- 📊 **任务驱动流程**: 将课程设计拆解为可视化任务节点，进度一目了然
- 💬 **流式对话交互**: 实时AI对话，内容流式生成到对应画布节点
- 📄 **多格式导出**: 支持画布快照(PNG/SVG)和结构化文档(DOCX/PDF)导出
- 🐳 **一键部署**: Docker容器化，5分钟完成本地部署

## 🎯 产品愿景 (第二阶段)

第二阶段将进行重大产品升级，采用现代AI Agent产品的主流设计模式（如Flowise.ai、Lovart）：

### 当前状态 (Phase 1) ✅
- [x] 智能三Agent架构：项目基础定义 → 评估框架设计 → 学习蓝图生成
- [x] 90秒快速生成：完整的PBL课程方案一键生成
- [x] 专业教学设计：基于Understanding by Design (UbD)框架
- [x] 质量保证体系：内置黄金标准案例验证

### 即将到来 (Phase 2) 🚧
- [ ] 无限画布界面：以任务节点方式组织课程设计流程
- [ ] 可视化工作流：智能任务分解和依赖关系展示
- [ ] 实时协作画布：节点-对话实时同步更新
- [ ] 专业级导出：画布快照 + 结构化文档双模式导出

## 🏗️ 技术架构

### 当前架构 (Phase 1)
```
前端界面 (HTML/JS) → FastAPI后端 → 三Agent工作流 → OpenAI GPT-4o
                                   ↓
              项目基础 → 评估框架 → 学习蓝图
```

### 目标架构 (Phase 2)
| 层级 | 技术选择 | 用途 |
|------|----------|------|
| **前端** | React 18 + TypeScript + Vite | 现代化前端框架 |
| **画布** | tldraw SDK 4.0+ | 专业级无限画布 |
| **AI对话** | assistant-ui | 企业级AI对话组件 |
| **状态管理** | Zustand | 轻量级状态管理 |
| **后端** | FastAPI + Python 3.10+ | 高性能API服务 |
| **AI引擎** | OpenAI GPT-4o | 课程设计智能引擎 |
| **文档导出** | @turbodocx/html-to-docx | 专业文档生成 |
| **部署** | Docker + Docker Compose | 容器化部署 |

### 系统架构图 (Phase 2)
```
┌─────────────────────────────────────────────────────────┐
│  任务面板    │          无限画布 (tldraw)          │  AI对话  │
│              │                                     │  侧边栏  │
│  ┌─────────┐ │  ┌──────┐    ┌──────┐    ┌──────┐ │         │
│  │进度追踪 │ │  │节点1 │───▶│节点2 │───▶│节点3 │ │  ┌────┐ │
│  │任务列表 │ │  │基础  │    │评估  │    │蓝图  │ │  │AI  │ │
│  └─────────┘ │  └──────┘    └──────┘    └──────┘ │  │助手│ │
│              │                                     │  └────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

- **Agent 1 - Genesis One**: 项目基础定义agent
- **Agent 2 - Genesis Two**: 评估框架设计agent
- **Agent 3 - Genesis Three**: 学习蓝图生成agent
- **工作流服务**: 串行协调三个Agent的执行
- **质量评估**: 基于黄金标准案例的输出质量评分

## 🚀 快速开始

### 环境要求

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) - 现代Python包管理器
- OpenAI API密钥

### 安装步骤

1. **安装uv（如果还没有）**
   ```bash
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **克隆项目**
   ```bash
   git clone <repository-url>
   cd eduagents
   ```

3. **设置后端环境**
   ```bash
   cd backend
   # 初始化uv项目并安装依赖
   uv sync
   ```

4. **配置环境变量**
   ```bash
   # .env文件已创建，编辑添加你的OpenAI API密钥
   # 修改 OPENAI_API_KEY 和 OPENAI_BASE_URL
   ```

5. **启动开发环境**

   **方式一：快速启动（推荐）**
   ```bash
   # 确保已配置.env文件后
   python quick_start.py
   ```

   **方式二：完整启动脚本**
   ```bash
   # 会自动检查uv和依赖
   python start_dev.py
   ```

   **方式三：手动启动**
   ```bash
   # 启动后端 (Terminal 1)
   cd backend
   uv run uvicorn app.main:app --reload

   # 启动前端 (Terminal 2)
   cd frontend
   python -m http.server 3000
   ```

6. **访问应用**
   - 前端界面: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

## 📋 使用指南

### 输入信息

在前端界面填写以下信息：

1. **课程主题**: 例如 "AI乐队制作人"
2. **课程概要**: 简要描述课程内容和项目目标
3. **年龄段**: 选择目标学生年龄段（6-18岁）
4. **课程时长**: 选择课程持续时间（1天-2周）
5. **AI工具**: 列出将使用的AI工具和技能

### 输出结果

系统将生成包含以下内容的完整PBL课程方案：

1. **项目基础定义**
   - 驱动性问题
   - 最终公开成果
   - 学习目标（硬技能+软技能）
   - 课程封面信息

2. **评估框架**
   - 4级评估量规（新手→学徒→工匠→大师）
   - 形成性检查点
   - 评估标准和时机

3. **学习蓝图**
   - 教师准备清单
   - 详细时间线和活动安排
   - 教师脚本和学生任务
   - 所需材料清单

## 🧪 测试

```bash
# 运行单元测试
cd backend
uv run pytest app/tests/ -v

# 运行特定测试
uv run pytest app/tests/test_workflow_service.py -v

# 运行黄金标准测试（需要API密钥）
uv run pytest app/tests/test_golden_standard.py::TestGoldenStandard::test_golden_standard_quality -v -s

# 运行测试并生成覆盖率报告
uv run pytest app/tests/ --cov=app --cov-report=html
```

## 📊 性能指标

根据PRD要求，系统性能目标：

- **总响应时间**: < 90秒
- **Agent 1**: < 20秒
- **Agent 2**: < 25秒
- **Agent 3**: < 40秒
- **质量得分**: > 80%（相对黄金标准）

## 📁 项目结构

```
eduagents/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── agents/         # 三个AI Agent
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置和服务
│   │   ├── models/         # 数据模型
│   │   └── tests/          # 测试文件
│   └── requirements.txt
├── frontend/                # 前端界面
│   └── index.html          # 单页面应用
├── docs/                    # 文档和基准案例
│   ├── prd.md              # 产品需求文档
│   └── 黄金标准方案.md      # 质量基准案例
├── CLAUDE.md               # Claude Code开发配置
├── start_dev.py            # 开发环境启动脚本
└── README.md
```

## 🔧 开发指南

### 使用uv管理开发环境

```bash
# 查看虚拟环境信息
cd backend && uv info

# 添加新的生产依赖
uv add requests

# 添加新的开发依赖
uv add --dev pytest-mock

# 更新所有依赖
uv sync --upgrade

# 进入虚拟环境shell
uv shell

# 运行代码质量检查
uv run black . && uv run isort . && uv run flake8

# 导出requirements.txt（如需要）
uv export --format requirements-txt --output requirements.txt
```

### 添加新Agent

1. 在`backend/app/agents/`创建新Agent类
2. 继承基础Agent模式，实现`generate()`方法
3. 在`workflow_service.py`中集成新Agent
4. 添加相应的测试文件: `uv run pytest app/tests/test_new_agent.py -v`

### API扩展

- 路由定义: `backend/app/api/routes.py`
- 数据模型: `backend/app/models/schemas.py`
- 配置管理: `backend/app/core/config.py`
- 测试新API: `uv run pytest app/tests/test_main.py -v`

### 前端定制

- 主要文件: `frontend/index.html`
- 样式和交互逻辑都在同一文件中
- 支持响应式设计和移动端适配

## 🎯 黄金标准案例

项目包含"AI乐队制作人"黄金标准案例，用于：

- **质量验证**: 确保生成内容达到专业标准
- **性能基准**: 测试系统响应时间和稳定性
- **持续改进**: 为Prompt优化提供参考依据

详见: `docs/黄金标准方案.md`

## 📈 未来路线图

### MVP阶段之外的功能
- 用户账户系统和方案保存
- 多语言支持
- 交互式方案编辑
- 更多教学法模板
- 协作功能

### 技术优化
- 响应式前端框架（React/Vue）
- 数据库持久化
- 容器化部署
- 性能监控和分析

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 👨‍💼 联系我们

- 项目维护者: AI Teaching Innovation Team
- 邮箱: [your-email@example.com]
- 项目主页: [GitHub Repository URL]

---

**让AI为教育赋能，让每一位教育者都能创造世界级课程！** 🎓✨