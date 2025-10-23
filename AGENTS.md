# AGENTS.md

## Project Overview
**eduagents（PBLCourseAgent）** 是一个AI驱动的PBL（项目式学习）课程设计助手。系统通过三个顺序执行的AI Agent自动生成高质量的教学方案，帮助教师快速设计符合UbD（逆向设计）框架的PBL课程。

**核心能力**：
- 从用户输入（主题、年级、时长、AI工具）自动生成完整课程设计
- 基于UbD框架设计评估标准和形成性检查点
- 生成可直接使用的课堂蓝图，包含教师脚本和学生任务

**当前阶段**：MVP Phase 1（三阶段工作流架构已完成）

---

## Agent Architecture

### 顺序工作流模式
```
User Input → Agent 1 → Agent 2 → Agent 3 → Final Output
           (基础定义)  (评估框架)  (学习蓝图)
```

**特点**：
- 简单的线性流水线（无并行、无循环）
- 每个Agent的输出是下一个Agent的输入
- 总响应时间：<90秒（目标）

---

### Agent 1: ProjectFoundationAgent

**位置**: `backend/app/agents/project_foundation_agent.py`

**角色**: "Genesis One" - 项目基础定义专家

**功能**: 定义PBL项目的核心框架

**输入**:
```json
{
  "course_topic": "课程主题",
  "course_overview": "课程概述",
  "age_group": "目标年龄段",
  "duration": "课程时长",
  "ai_tools": "使用的AI工具（逗号分隔）"
}
```

**输出**:
```json
{
  "drivingQuestion": "驱动性问题",
  "publicProduct": {
    "description": "公开成果描述",
    "components": ["成果组成部分列表"]
  },
  "learningObjectives": {
    "hardSkills": ["硬技能列表"],
    "softSkills": ["软技能列表"]
  },
  "coverPage": {
    "courseTitle": "课程标题",
    "tagline": "副标题",
    "ageGroup": "年龄段",
    "duration": "时长",
    "aiTools": "AI工具"
  }
}
```

**LLM配置**:
- Model: `settings.agent1_model` or `settings.openai_model` (默认: deepseek-chat)
- Temperature: 0.7
- Max Tokens: 2000
- Timeout: 20秒

**Prompt版本**: 参见 `backend/app/prompts/phr/project_foundation_v1.md`

---

### Agent 2: AssessmentFrameworkAgent

**位置**: `backend/app/agents/assessment_framework_agent.py`

**角色**: "Genesis Two" - 评估框架设计专家

**功能**: 基于项目基础设计UbD评估体系

**输入**: Agent 1的完整输出（ProjectFoundation JSON）

**输出**:
```json
{
  "summativeRubric": [
    {
      "dimension": "评估维度",
      "level_1_desc": "新手水平描述",
      "level_2_desc": "学徒水平描述",
      "level_3_desc": "工匠水平描述",
      "level_4_desc": "大师水平描述"
    }
  ],
  "formativeCheckpoints": [
    {
      "name": "检查点名称",
      "triggerTime": "触发时间",
      "purpose": "检查目的"
    }
  ]
}
```

**LLM配置**:
- Model: `settings.agent2_model` or `settings.openai_model`
- Temperature: 0.6
- Max Tokens: 2500
- Timeout: 25秒

**Prompt版本**: 参见 `backend/app/prompts/phr/assessment_framework_v1.md`

---

### Agent 3: LearningBlueprintAgent

**位置**: `backend/app/agents/learning_blueprint_agent.py`

**角色**: "Genesis Three" - 课堂蓝图生成专家

**功能**: 综合前两个Agent的输出，生成详细的课堂实施方案

**输入**:
- Agent 1的输出（ProjectFoundation）
- Agent 2的输出（AssessmentFramework）

**输出**:
```json
{
  "teacherPrep": {
    "materialList": ["材料清单"],
    "skillPrerequisites": ["教师技能前提"]
  },
  "timeline": [
    {
      "timeSlot": "时间段",
      "activityTitle": "活动标题",
      "teacherScript": "教师脚本",
      "studentTask": "学生任务",
      "materials": ["本活动所需材料"]
    }
  ]
}
```

**LLM配置**:
- Model: `settings.agent3_model` or `settings.openai_model`
- Temperature: 0.6
- Max Tokens: 4000
- Timeout: 40秒

**Prompt版本**: 参见 `backend/app/prompts/phr/learning_blueprint_v1.md`

---

## Project Structure

```
eduagents/
├── backend/                 # Python + FastAPI后端
│   ├── app/
│   │   ├── agents/          # 三个AI Agent实现
│   │   │   ├── __init__.py
│   │   │   ├── project_foundation_agent.py    # Agent 1
│   │   │   ├── assessment_framework_agent.py  # Agent 2
│   │   │   └── learning_blueprint_agent.py    # Agent 3
│   │   ├── api/             # FastAPI路由
│   │   │   └── routes.py
│   │   ├── core/            # 核心配置和工具
│   │   │   ├── config.py    # 环境配置
│   │   │   └── openai_client.py  # OpenAI客户端封装
│   │   ├── prompts/         # Prompt管理（新增）
│   │   │   ├── phr/         # Prompt History Records
│   │   │   └── schemas/     # JSON Schema定义
│   │   ├── services/        # AI服务和业务逻辑
│   │   │   └── ai_service.py
│   │   ├── models/          # 数据模型
│   │   └── tests/           # 后端测试
│   ├── pyproject.toml       # uv项目配置
│   ├── .env                 # 环境变量（不提交）
│   └── main.py
├── frontend-x/              # React + Ant Design X前端（V3）
│   ├── src/
│   │   ├── components/      # React组件（ChatPanel, ContentPanel等）
│   │   ├── services/        # API调用服务
│   │   ├── stores/          # Zustand状态管理
│   │   ├── hooks/           # Custom Hooks
│   │   ├── types/           # TypeScript类型定义
│   │   └── constants/       # 常量（UbD定义等）
│   └── package.json
├── docs/                    # 文档和基准案例
├── AGENTS.md               # 本文件（机器可读文档）
├── CLAUDE.md               # 开发配置和质量标准
└── README.md               # 人类可读文档
```

---

## Setup Instructions

### 环境要求
- Python 3.10+
- Node.js 18+ (前端)
- uv (Python包管理器)

### 后端设置

```bash
# 1. 进入后端目录
cd backend

# 2. 初始化uv项目（首次运行）
uv sync

# 3. 配置环境变量
# 创建 .env 文件（从 .env.example 复制）
cp .env.example .env

# 编辑 .env，添加必需的配置：
# PBL_AI_API_KEY=your_api_key_here
# PBL_AI_MODEL=deepseek-chat
# PBL_AI_BASE_URL=http://your-service-url/v1

# 4. 启动开发服务器
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 48097
```

**API访问**: http://localhost:48097/docs (Swagger文档)

### 前端设置（V3）

```bash
cd frontend-x
npm install
npm run dev
```

**前端访问**: http://localhost:48098

---

## Environment Variables

**必需变量** (在 `backend/.env` 中配置):

```bash
# AI服务配置（使用PBL专用前缀避免冲突）
PBL_AI_API_KEY=your_api_key        # 必需
PBL_AI_MODEL=deepseek-chat         # 推荐：deepseek-chat或gpt-4o
PBL_AI_BASE_URL=http://xxx/v1      # API基础URL

# 可选：为不同Agent配置不同模型
AGENT1_MODEL=deepseek-chat
AGENT2_MODEL=deepseek-chat
AGENT3_MODEL=gpt-4o

# 数据库（默认使用SQLite）
DATABASE_URL=sqlite:///./app.db
```

**配置优先级**:
1. 环境变量（`.env`文件）
2. 默认值（`backend/app/core/config.py`）

---

## Build and Run Commands

### 开发模式

```bash
# 后端开发服务器
cd backend
uv run uvicorn app.main:app --reload

# 运行特定测试
uv run pytest app/tests/test_project_foundation_agent.py -v

# 运行所有测试
uv run pytest app/tests/ -v

# 代码质量检查
uv run black .
uv run isort .
uv run flake8
```

### 依赖管理

```bash
# 添加新依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name

# 更新依赖
uv sync --upgrade

# 查看依赖树
uv pip list
```

---

## Development Workflow

### 标准开发流程

1. **创建功能分支**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **开发和测试**
   ```bash
   # 修改代码
   # 运行测试确保不破坏现有功能
   uv run pytest app/tests/ -v
   ```

3. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 描述你的改动"
   ```

4. **创建PR**
   ```bash
   git push origin feat/your-feature-name
   # 然后在GitHub创建Pull Request
   ```

### Prompt修改流程

**重要**: Prompt是Agent的核心逻辑，修改必须谨慎！

1. **找到对应的PHR文件**
   - Agent 1: `backend/app/prompts/phr/project_foundation_v1.md`
   - Agent 2: `backend/app/prompts/phr/assessment_framework_v1.md`
   - Agent 3: `backend/app/prompts/phr/learning_blueprint_v1.md`

2. **创建新版本**
   ```bash
   # 不要直接修改v1，而是创建v2
   cp backend/app/prompts/phr/project_foundation_v1.md \
      backend/app/prompts/phr/project_foundation_v2.md
   ```

3. **更新新版本**
   - 修改Prompt内容
   - 更新Meta信息（版本号、修改日期、修改原因）
   - 添加Change Log条目

4. **更新Agent代码引用**
   ```python
   # 在 project_foundation_agent.py 中
   # 更新 _build_system_prompt() 方法以加载新版本
   ```

5. **运行回归测试**
   ```bash
   uv run pytest app/tests/test_project_foundation_agent.py -v
   ```

6. **记录性能指标**
   - 在PHR文件的Meta部分记录新版本的性能表现

---

## Code Style and Conventions

### Python
- **格式化**: black (行宽: 120)
- **导入排序**: isort
- **Linter**: flake8
- **类型提示**: 鼓励使用，但不强制

### 命名规范
- **类**: PascalCase (如 `ProjectFoundationAgent`)
- **函数/方法**: snake_case (如 `generate_response`)
- **私有方法**: _前缀 (如 `_build_system_prompt`)
- **常量**: UPPER_SNAKE_CASE

### 注释规范
- 模块级: 使用docstring说明模块用途
- 类级: 说明类的职责
- 方法级: 使用docstring描述参数、返回值、异常
- 行内注释: 仅在必要时使用，解释"为什么"而非"做什么"

---

## Architecture Notes

### 关键架构决策

**1. 为什么使用顺序工作流而非并行？**
- MVP阶段，三个Agent有严格的依赖关系（Agent 2依赖Agent 1的输出）
- 顺序流简单、可预测、易调试
- 总时间<90秒，性能满足需求

**2. 为什么每个Agent独立定义Prompt？**
- 各Agent的角色和输出完全不同
- 独立Prompt便于单独优化和A/B测试
- 避免单一Prompt过于复杂

**3. 为什么使用OpenAI兼容API而非封装SDK？**
- 直接调用API简洁清晰
- 无额外抽象层，性能更好
- 兼容多种LLM提供商（OpenAI、DeepSeek等）

**4. Phase 2画布架构考虑**
- 前端迁移到tldraw无限画布
- 可能引入非线性交互（用户修改中间结果）
- 届时考虑引入Agent间协议规范（YAML）

---

## Testing Strategy

### 测试层级

**1. 单元测试** (覆盖率目标: >80%)
- 每个Agent独立测试
- Mock OpenAI API调用
- 验证Prompt构建逻辑
- 验证JSON解析逻辑

**2. 集成测试**
- 测试三个Agent的顺序工作流
- 使用真实API调用（受控环境）
- 验证数据在Agent间正确传递

**3. 黄金标准测试**
- 使用预定义的高质量课程案例
- 比较AI输出与黄金标准的匹配度（目标: >80%）

### 运行测试

```bash
# 所有测试
uv run pytest app/tests/ -v

# 单个Agent测试
uv run pytest app/tests/test_project_foundation_agent.py -v

# 带覆盖率报告
uv run pytest app/tests/ --cov=app --cov-report=html
```

---

## Deployment

**当前阶段**: 本地开发/测试

**计划部署方式** (Phase 2后):
- 后端: Docker容器 + 云平台（待定）
- 前端: Vercel或类似静态托管
- 数据库: 从SQLite迁移到PostgreSQL

**环境配置**:
- 开发环境: `.env.development`
- 生产环境: 环境变量（不使用.env文件）

---

## Common Tasks

### 添加新Agent

1. 在 `backend/app/agents/` 创建新Agent类
2. 在 `backend/app/prompts/phr/` 创建PHR文件
3. 更新工作流服务以集成新Agent
4. 添加对应的单元测试
5. 更新本文档（AGENTS.md）

### 修改Agent输出Schema

1. 在PHR文件中更新Schema定义
2. 修改Agent代码中的解析逻辑
3. 更新所有依赖此输出的下游Agent
4. 更新测试用例
5. 运行回归测试确保兼容性

### 调试Agent输出异常

```bash
# 1. 检查API调用日志
# 日志位置: backend/app/logs/ (如果配置了)

# 2. 运行单个Agent测试并查看详细输出
uv run pytest app/tests/test_xxx_agent.py -v -s

# 3. 检查Prompt是否符合预期
# 在Agent代码中临时添加print语句输出完整Prompt

# 4. 使用OpenAI Playground测试Prompt
# 复制生成的Prompt到Playground验证
```

---

## Gotchas and Known Issues

### 1. JSON解析失败
**症状**: Agent返回成功但JSON解析失败

**原因**: LLM有时返回带Markdown代码块的JSON

**解决方案**: Agent代码已包含自动提取逻辑（第119-128行）

### 2. 超时问题
**症状**: Agent调用超时（>20/25/40秒）

**可能原因**:
- API服务响应慢
- Prompt过长
- max_tokens设置过高

**解决方案**:
- 在 `.env` 中调整各Agent的timeout设置
- 优化Prompt长度
- 降低max_tokens（如果合理）

### 3. 环境变量冲突
**症状**: 使用了错误的API Key或Model

**原因**: 系统中其他项目使用标准环境变量名（OPENAI_API_KEY）

**解决方案**: eduagents使用专用前缀 `PBL_AI_*`，确保 `.env` 配置正确

### 4. uv命令不工作
**症状**: `uv: command not found`

**解决方案**:
```bash
# 安装uv
pip install uv

# 或使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Permissions and Safety

### AI Agent自主权限

**无需询问可以执行**:
- 读取 `backend/app/` 下的所有代码
- 运行测试: `uv run pytest`
- 代码格式化: `black`, `isort`
- 查看文档和配置文件

**需要确认才能执行**:
- 修改Prompt文件（`backend/app/prompts/phr/`）
- 创建新的Agent
- 修改API路由
- 更改环境配置（`config.py`）
- 修改数据库模型
- 安装新依赖（`uv add`）

**禁止操作**:
- 提交 `.env` 文件到git
- 直接修改生产环境配置
- 删除测试文件
- 硬编码API密钥

---

## Quick Reference

**启动后端**: `cd backend && uv run uvicorn app.main:app --reload`

**运行测试**: `uv run pytest app/tests/ -v`

**API文档**: http://localhost:48097/docs

**Prompt位置**: `backend/app/prompts/phr/`

**配置文件**: `backend/app/core/config.py` + `backend/.env`

**Git提交格式**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `perf:`

---

## Contact and Resources

**项目仓库**: (待添加Git仓库URL)

**相关文档**:
- [CLAUDE.md](./CLAUDE.md) - 开发配置和质量标准
- [README.md](./README.md) - 项目概述和用户文档
- [docs/](./docs/) - 详细技术文档

**外部资源**:
- [uv文档](https://docs.astral.sh/uv/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [OpenAI API文档](https://platform.openai.com/docs)
