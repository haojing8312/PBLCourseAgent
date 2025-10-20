# Implementation Plan: UbD-PBL 课程架构师 V3

**Branch**: `001-ubd-pbl-architect-v3` | **Date**: 2025-10-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ubd-pbl-architect-v3/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

将现有PBL课程生成器升级为专业的UbD-PBL课程架构师。通过重构三个现有Agent(ProjectFoundation、AssessmentFramework、LearningBlueprint)并增强前端UX,实现:

1. **UbD理论内嵌化**: 在UI的G/U/Q/K/S输入卡片上显示解释性说明,帮助教师理解每个元素的UbD定义
2. **AI生成质量保障**: 强化Agent Prompt,确保生成的U是抽象观点(非知识点)、驱动性问题包含PBL属性、学习蓝图标注UbD目标和WHERETO原则
3. **PBL阶段明确化**: 学习蓝图从线性逐日计划改为PBL经典阶段结构(项目启动→知识构建→开发迭代→成果展示)
4. **编辑与联动**: 用户可编辑任意模块内容,系统检测变更并提示重新生成下游内容
5. **导出优化**: 生成的Markdown教案包含理论说明引言,清晰体现UbD逆向设计逻辑

**技术方法**:
- 后端:创建新版本的Agent Prompt(PHR v2)并升级现有三个Agent类,增加对话历史存储
- 前端:**完全重构为ChatGPT风格对话式UI**,采用顶部步骤导航+左侧对话窗口(40%)+右侧内容预览编辑区(60%),基于Ant Design X组件库构建
- 数据模型:扩展现有CourseProject/StageData实体,添加UbD目标标签、WHERETO原则标签、对话历史字段

## Technical Context

**Language/Version**: Python 3.10+, TypeScript 4.9+
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Python SDK, SQLAlchemy(for SQLite ORM), Pydantic
- Frontend: React 18, TypeScript, Ant Design X(AI对话组件库), Ant Design 5.x, Zustand(state management), Vite, CodeMirror 6(Markdown编辑), react-markdown + remark-gfm(Markdown预览)
**Storage**: SQLite(MVP phase, schema defined in backend/app/models/), 课程项目JSON数据存储在database
**Testing**:
- Backend: pytest + Fastapi.testclient, 黄金标准案例对比测试
- Frontend: Vitest + React Testing Library
**Target Platform**:
- Backend: Linux/Windows服务器(开发时本地Windows)
- Frontend: 现代浏览器(Chrome/Firefox/Safari/Edge最新版), 响应式设计支持桌面和平板
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**:
- 单个Agent响应时间<20-40秒(根据PRD)
- 完整三阶段workflow<90秒
- AI生成内容质量≥80%黄金标准匹配度
- 支持100并发用户,AI响应P95≤15秒
**Constraints**:
- AI生成依赖外部服务(OpenAI或兼容API),需处理网络超时和服务不可用
- 前端采用ChatGPT风格对话式UI,需实现流式SSE消息显示和Markdown实时预览
- 必须向后兼容现有V2版本的课程数据格式(或提供迁移脚本)
- 对话历史需持久化到数据库,每个步骤独立存储
**Scale/Scope**:
- 预期用户规模:初期<1000教师用户
- 单个课程项目数据:<1MB(G/U/Q/K/S各<10项,PBL蓝图<20周)
- 8个核心数据实体(CourseProject, 3个StageData, PerformanceTask, Rubric, LearningActivity, ExportTemplate)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Linus-Style Code Review Philosophy ✅ PASS

**Evaluation**:
- ✅ 特殊情况消除: UbD三阶段workflow设计消除了"用户不知道下一步做什么"的特殊情况,通过固定流程(Stage1→2→3)替代复杂的状态机
- ✅ 数据结构优先: 核心设计围绕8个实体(CourseProject, StageData等)展开,通过关系型设计自然表达阶段依赖,避免if/else判断阶段状态
- ✅ 向后兼容: 扩展现有StageData实体而非重写,确保V2数据可迁移
- ✅ 简洁性: 三Agent架构保持不变,仅升级Prompt版本(v1→v2),避免重构整个系统

**No violations**

### II. Test-First Development (NON-NEGOTIABLE) ✅ PASS

**Evaluation**:
- ✅ 计划包含测试策略: 后端pytest+黄金标准案例,前端Vitest
- ✅ 黄金标准强制: Agent输出必须≥80%匹配度
- ✅ 覆盖率要求: >80% coverage明确写入Success Criteria

**Implementation Note**: 在tasks.md生成时,将为每个FR创建对应测试任务,且测试任务优先级高于实现任务

**No violations**

### III. Transparent Error Handling ✅ PASS

**Evaluation**:
- ✅ 明确错误处理需求: FR-033要求AI生成失败时显示具体错误并提供重试选项
- ✅ 无降级回复: Edge Case中明确"AI服务不可用时显示错误信息",不使用占位内容
- ✅ 前端错误展示: FR-032要求显示加载状态,FR-033要求显示错误详情

**No violations**

### IV. Prompt as Code (PHR Standard) ✅ PASS

**Evaluation**:
- ✅ 版本化计划: Summary明确提到"创建新版本的Agent Prompt(PHR v2)"
- ✅ 现有PHR基础: 项目已有backend/app/prompts/phr/*_v1.md文件
- ✅ 三Agent分离Prompt: FR-028/029/030分别定义三个Agent的角色和Prompt重点

**Implementation Note**: Phase 1将创建:
- `backend/app/prompts/phr/project_foundation_v2.md`
- `backend/app/prompts/phr/assessment_framework_v2.md`
- `backend/app/prompts/phr/learning_blueprint_v2.md`

**No violations**

### V. Agent-Driven Architecture ✅ PASS

**Evaluation**:
- ✅ 三Agent workflow保持: 仍然是ProjectFoundation → AssessmentFramework → LearningBlueprint
- ✅ 性能要求明确: Performance Goals中<20-40s per agent, <90s total
- ✅ 质量要求: ≥80%黄金标准匹配度
- ✅ 契约不变性: 扩展StageData实体字段而非破坏现有接口

**No violations**

### VI. UbD Framework Fidelity ✅ PASS (CORE FEATURE)

**Evaluation**:
- ✅ **这是本feature的核心目标**: 整个V3升级就是为了强化UbD框架的保真度
- ✅ 逆向设计明确化: FR-001-006(模块1),FR-007-013(模块2),FR-014-019(模块3)严格按UbD三阶段组织
- ✅ Essential Questions强制: FR-004要求AI生成开放性基本问题
- ✅ 评估先行: FR-011要求详细Rubric,FR-018要求学习活动与评估任务时间对齐
- ✅ 四级量规: Spec未明确4级,但FR-011要求"4-5个评分等级",符合宪法要求

**This feature STRENGTHENS constitutional compliance**

### VII. Simplicity and Pragmatism ✅ PASS

**Evaluation**:
- ✅ 增量改进: 在现有三Agent基础上升级,不引入新的复杂抽象层
- ✅ 依赖合理: 仅使用已有依赖(FastAPI, React, tldraw),无新框架
- ✅ YAGNI: Spec明确FR-023(PDF导出)为"可选,P3优先级",FR-024-027(项目管理)为P3,专注核心workflow
- ✅ 简单数据结构: 8个实体清晰,无过度抽象

**No violations**

### Quality Standards ✅ PASS

**Evaluation**:
- ✅ 测试覆盖: >80% coverage required
- ✅ 代码质量工具: Backend(black,isort,flake8), Frontend(ESLint,Prettier)已配置
- ✅ AI质量验证: 黄金标准≥80%, UbD元素验证(FR-003/004/005)
- ✅ 性能基准: <90s workflow明确

**No violations**

### GATE STATUS: ✅ PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```
specs/001-ubd-pbl-architect-v3/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already created)
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
├── research.md          # Phase 0 output (generated below)
├── data-model.md        # Phase 1 output (generated below)
├── quickstart.md        # Phase 1 output (generated below)
├── contracts/           # Phase 1 output (generated below)
│   ├── openapi.yaml     # API contract for all endpoints
│   └── README.md        # Contract usage guide
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**选择结构**: Web application (frontend + backend)

```
backend/
├── app/
│   ├── agents/                      # AI Agent implementations
│   │   ├── project_foundation.py    # Agent 1 - 需升级prompt
│   │   ├── assessment_framework.py  # Agent 2 - 需升级prompt
│   │   └── learning_blueprint.py    # Agent 3 - 需升级prompt
│   ├── prompts/phr/                 # Prompt History Records
│   │   ├── project_foundation_v2.md      # 新建 (Phase 1)
│   │   ├── assessment_framework_v2.md    # 新建 (Phase 1)
│   │   └── learning_blueprint_v2.md      # 新建 (Phase 1)
│   ├── api/                         # FastAPI routes
│   │   └── v1/
│   │       ├── course.py            # 课程项目CRUD - 需扩展编辑功能
│   │       └── generate.py          # AI生成endpoints - 需增强错误处理
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── course_project.py        # 需扩展: 添加change_tracking字段
│   │   ├── stage_data.py            # 需扩展: 添加ubd_labels, whereto_labels
│   │   ├── performance_task.py      # 已存在或新建
│   │   ├── rubric.py                # 已存在或新建
│   │   └── learning_activity.py    # 新建
│   ├── services/                    # Business logic
│   │   ├── workflow_service.py      # 需扩展: 变更检测和联动重生成逻辑
│   │   ├── export_service.py        # 需扩展: 新Markdown模板格式
│   │   └── validation_service.py   # 新建: UbD元素验证(U是观点非知识点等)
│   └── tests/
│       ├── test_agents/             # Agent单元测试 - 需更新v2 prompt测试
│       ├── test_api/                # API集成测试
│       └── golden_standards/        # 黄金标准案例
├── pyproject.toml                   # uv配置
└── .env.example                     # 环境变量模板

frontend-x/                          # 全新ChatGPT风格对话式前端
├── src/
│   ├── components/
│   │   ├── StepNavigator.tsx        # 新建: 顶部步骤导航组件([1.锚定理解✓]→[2.评估证据]...)
│   │   ├── ChatPanel.tsx            # 新建: 左侧对话面板(40%宽度)
│   │   │                            #   - 使用Ant Design X <Conversations>组件
│   │   │                            #   - 显示AI流式回复和用户对话历史
│   │   │                            #   - 集成<Sender>输入框和<Prompts>建议
│   │   ├── ContentPanel.tsx         # 新建: 右侧内容面板(60%宽度)
│   │   │                            #   - 包含预览/编辑模式切换按钮
│   │   │                            #   - 显示依赖提示(如"正在基于步骤1的3个U生成...")
│   │   ├── MarkdownPreview.tsx      # 新建: Markdown预览模式
│   │   │                            #   - 使用react-markdown渲染
│   │   │                            #   - 支持UbD元素高亮(U/Q/K等)
│   │   ├── MarkdownEditor.tsx       # 新建: Markdown编辑模式
│   │   │                            #   - 使用CodeMirror 6实现
│   │   │                            #   - 语法高亮、自动保存
│   │   ├── DownloadButton.tsx       # 新建: 下载课程方案按钮(步骤4)
│   │   └── UbdTooltip.tsx           # 新建: UbD元素解释tooltip
│   │                                #   - G/U/Q/K/S每个元素的理论说明
│   ├── hooks/
│   │   ├── useStepWorkflow.ts       # 新建: 步骤流程管理hook
│   │   │                            #   - 控制步骤进入/完成状态
│   │   │                            #   - 串行流程控制(必须完成N才能进N+1)
│   │   ├── useChatConversation.ts   # 新建: 对话管理hook
│   │   │                            #   - 集成Ant Design X useXChat
│   │   │                            #   - 对接后端SSE流式API
│   │   │                            #   - 持久化对话历史到数据库
│   │   └── useMarkdownSync.ts       # 新建: Markdown同步hook
│   │                                #   - 实时保存编辑内容到后端
│   │                                #   - 检测变更触发联动提示
│   ├── services/
│   │   ├── workflowService.ts       # 扩展: SSE流式workflow API调用
│   │   ├── conversationService.ts   # 新建: 对话历史CRUD
│   │   └── exportService.ts         # 扩展: 下载Markdown/PDF
│   ├── stores/                      # Zustand state
│   │   └── courseStore.ts           # 扩展: 新增字段
│   │                                #   - currentStep: 1|2|3|4
│   │                                #   - stepStatus: Record<number, 'pending'|'generating'|'completed'>
│   │                                #   - conversationHistory: Record<number, Message[]>
│   │                                #   - stageMarkdowns: Record<number, string>
│   │                                #   - isEditMode: boolean
│   ├── types/
│   │   ├── course.ts                # 扩展: 新字段类型定义
│   │   └── conversation.ts          # 新建: 对话消息类型定义
│   ├── constants/
│   │   └── ubdDefinitions.ts        # 新建: UbD理论定义常量
│   │                                #   - G/U/Q/K/S的解释说明文本
│   │                                #   - WHERETO原则说明
│   └── utils/
│       └── ubdValidation.ts         # 新建: 前端UbD验证辅助函数
├── package.json                     # 新增依赖: @ant-design/x, @ant-design/pro-editor, @uiw/react-codemirror
└── vite.config.ts

docs/                                # 文档和标准案例
├── UBD教案模板.md                   # 新Markdown模板(需更新)
├── ubd教案案例一.md                 # 黄金标准案例
└── specs/                           # Feature specs (本目录)
```

**Structure Decision**:
- **前端完全重构**: 从`frontend-v2/`(tldraw无限画布)迁移到`frontend-x/`(ChatGPT风格对话式UI)
  - **理由**: UbD课程设计是**串行的逆向设计流程**(阶段1→2→3),更适合步骤引导而非自由画布
  - **用户体验**: 左侧对话窗口让用户自然地与AI交流修改意图,右侧内容区实时预览/编辑,符合现代AI产品交互习惯
  - **技术栈**: Ant Design X提供开箱即用的AI对话组件(`<Conversations>`,`useXChat`),大幅减少自定义开发量
- 后端保持现有结构,主要修改:
  - Agent类升级prompt引用(PHR v2)
  - 新增API: `POST /api/v1/courses/{id}/conversation`(对话历史持久化)
  - 扩展models: CourseProject添加`conversation_history`字段
  - 新增services: `validation_service.py`(UbD元素验证), `conversation_service.py`(对话管理)
- 新增文件较多但结构清晰,所有组件职责单一,符合React最佳实践

## Complexity Tracking

**无违规项需要说明** - 所有设计符合Constitution要求


