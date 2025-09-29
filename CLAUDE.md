# Project Genesis AI - Claude Code 开发配置

## 项目概述
这是一个基于AI的PBL（项目式学习）课程生成器MVP，能够自动生成高质量的教学方案。

## 技术架构
- **后端**: Python 3.10+ + FastAPI + OpenAI API
- **前端**: React + TypeScript + Vite
- **数据库**: SQLite (MVP阶段)
- **AI引擎**: OpenAI GPT-4o API

## 开发标准

### 代码风格
- **Python**: 使用 black, isort, flake8
- **JavaScript/TypeScript**: ESLint + Prettier
- **函数命名**: 使用描述性名称，遵循各语言惯例
- **注释**: 仅在必要时添加，代码应自说明

### 测试策略
- **后端测试**: pytest + fastapi.testclient
- **前端测试**: Vitest + React Testing Library
- **集成测试**: 使用黄金标准案例验证输出质量
- **测试覆盖率**: 目标 >80%

### 项目结构
```
eduagents/
├── backend/
│   ├── app/
│   │   ├── agents/          # 三个AI Agent实现
│   │   ├── api/             # FastAPI路由
│   │   ├── core/            # 核心配置和工具
│   │   ├── models/          # 数据模型
│   │   └── tests/           # 后端测试
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API调用
│   │   ├── types/           # TypeScript类型定义
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # 文档和基准案例
├── tests/                   # 集成测试
└── CLAUDE.md               # 此文件
```

### Git 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- test: 测试相关
- refactor: 代码重构
- perf: 性能优化

### 环境变量
创建 `.env` 文件包含:
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
DATABASE_URL=sqlite:///./app.db
```

### 开发命令
```bash
# 后端开发 - 使用uv进行环境隔离和包管理
cd backend

# 初始化uv项目（首次运行）
uv sync

# 激活虚拟环境并启动服务
uv run uvicorn app.main:app --reload

# 或者进入虚拟环境shell
uv shell
uvicorn app.main:app --reload

# 前端开发
cd frontend
python -m http.server 3000

# 运行测试
cd backend
uv run pytest
# 或运行特定测试
uv run pytest app/tests/test_workflow_service.py -v

# 代码质量检查
cd backend
uv run black .
uv run isort .
uv run flake8

# 添加新依赖
uv add package_name
# 添加开发依赖
uv add --dev package_name

# 更新依赖
uv sync --upgrade
```

### 质量标准
1. 所有代码必须通过测试
2. 遵循PRD中定义的性能指标（总响应时间<90秒）
3. AI生成内容必须达到黄金标准案例80%匹配度
4. 代码review通过且无安全漏洞

### Agent开发指南
每个Agent都应该：
1. 有清晰的角色定义和Prompt模板
2. 输入输出格式严格遵循PRD规范
3. 包含错误处理和重试机制
4. 有对应的单元测试

### 部署注意事项
- 不提交API密钥到git
- 生产环境使用环境变量管理配置
- 实施适当的API速率限制
- 记录API调用日志用于监控

## 开发优先级
按照PRD中的阶段顺序开发：
1. Agent 1: 项目基础定义
2. Agent 2: 评估框架设计
3. Agent 3: 学习蓝图生成
4. 前端界面集成
5. 质量测试和优化