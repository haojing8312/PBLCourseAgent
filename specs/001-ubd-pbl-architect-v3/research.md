# Research: UbD-PBL 课程架构师 V3

**Feature**: UbD-PBL 课程架构师 V3
**Date**: 2025-10-20
**Status**: Research Complete

## Purpose

本文档记录了所有技术决策的研究过程和理由,解决了Technical Context中的所有未确定项,并为Phase 1设计提供依据。

## Research Areas

### 1. UbD理论嵌入UX的最佳实践

**Research Question**: 如何在UI中有效展示教育学概念解释,既不干扰用户操作流程,又能真正帮助理解?

**调研过程**:
- 研究了Khan Academy, Coursera等教育平台的"学习提示"设计模式
- 分析了Notion, Airtable等工具中的上下文帮助(contextual help)实现
- 参考了Material Design的Tooltip和Dialog组件使用指南

**Decision**: 采用**分层帮助系统**
1. **一级提示**: 输入卡片上方的简短说明(1-2句话,始终可见)
2. **二级帮助**: 点击"?"图标展开的详细解释浮层(包含示例对比)
3. **三级引导**: 首次进入模块时的onboarding overlay(可跳过和关闭)

**Rationale**:
- 一级提示不占额外空间,满足FR-001"简短精炼"要求
- 二级帮助可选展开,避免信息过载,适合新手深入学习
- 三级引导解决User Story 2"首次使用理解UbD"的场景

**Alternatives Considered**:
- ❌ 完全依赖外部文档链接: 用户不会点击,学习成本高
- ❌ 强制弹窗讲解: 打断流程,用户体验差
- ❌ 视频教程: 制作和维护成本高,不适合MVP

**Implementation Note**:
- 前端组件: `TooltipHelper.tsx`(一级), `HelpDialog.tsx`(二级), `OnboardingOverlay.tsx`(三级)
- 说明文本存储: `frontend-x/src/constants/ubdDefinitions.ts`(便于多语言扩展)

---

### 2. AI生成内容的UbD对齐验证方法

**Research Question**: 如何自动化验证AI生成的U是"抽象观点"而非"具体知识点"?

**调研过程**:
- 研究了NLP语义分类任务的常见方法(关键词匹配 vs 语义embedding)
- 分析了现有教育学文献中U vs K的判别特征
- 参考了OpenAI GPT-4的Few-shot classification能力

**Decision**: 采用**两层验证策略**
1. **规则层(快速否决)**: 关键词黑名单检测
   - 如果U包含"掌握"、"学会"、"会使用"等动词→标记为疑似K
   - 如果U包含具体工具名(如"Python"、"TensorFlow")而非抽象概念→标记为疑似K
2. **语义层(AI判别)**: 调用小模型(如GPT-3.5 or local model)进行二次分类
   - Prompt: "判断以下陈述是'抽象的持久理解'还是'具体的知识点':[待判别文本]"
   - 返回置信度,<70%置信度时触发前端警告"此条目可能更适合作为K而非U"

**Rationale**:
- 规则层成本低,能过滤明显错误(满足Edge Case"理论对齐失败"处理需求)
- 语义层提高准确率,避免误判抽象表述的U
- 警告而非强制阻止,保留教师最终决策权(符合Pragmatism原则)

**Alternatives Considered**:
- ❌ 仅规则层: 漏报率高,复杂表述无法处理
- ❌ 完全依赖大模型: 成本高,响应慢,不适合实时验证
- ❌ 不验证,完全信任Agent输出: 违反FR-003要求

**Implementation Note**:
- 后端: `backend/app/services/validation_service.py::validate_understanding_vs_knowledge()`
- 规则配置: `backend/app/config/ubd_rules.yaml`
- 语义模型: 复用现有AI service,增加classification endpoint

---

### 3. PBL阶段划分的行业标准与灵活性平衡

**Research Question**: PBL的"经典阶段"应该强制固定(如4个阶段)还是允许教师自定义?

**调研过程**:
- 研究了Buck Institute for Education(PBL权威机构)的阶段划分标准
- 分析了PBLWorks, Edutopia等平台的项目模板
- 参考了Scrum, Design Thinking等相关方法论的阶段设计

**Decision**: 采用**预设模板+有限自定义**
- **预设模板**: 4个标准PBL阶段(满足FR-014要求)
  1. 项目启动 (Project Launch) - 对应WHERETO的H(Hook)
  2. 知识与技能构建 (Knowledge & Skill Building) - 对应E(Explore), E(Equip)
  3. 开发与迭代 (Development & Iteration) - 对应R(Rethink), T(Tailor)
  4. 成果展示与反思 (Presentation & Reflection) - 对应O(Organize)
- **有限自定义**: 允许重命名阶段,调整时长,添加/删除活动,但不允许打乱阶段顺序(保持逆向设计逻辑)

**Rationale**:
- 预设模板降低新手教师认知负担,符合UbD框架要求
- 有限自定义满足专业教师个性化需求,平衡灵活性与规范性
- 阶段顺序不可打乱确保UbD逻辑不被破坏(符合Constitution VI)

**Alternatives Considered**:
- ❌ 完全固定: 不适合不同学科和课时安排
- ❌ 完全自由: 用户可能创建违背UbD逻辑的流程,失去专业性
- ❌ 多种预设模板(如6周版,12周版): MVP阶段过于复杂,YAGNI

**Implementation Note**:
- 数据模型: `LearningActivity.phase_type`字段限制为enum(launch, build, develop, present)
- 前端组件: `StageThreeForm.tsx`展示4个折叠面板,每个面板对应一个阶段
- 导出模板: `docs/UBD教案模板.md`明确包含4个阶段的Markdown结构

---

### 4. 编辑联动重生成的粒度控制

**Research Question**: 当用户修改模块1的某个U时,应该重新生成整个模块2还是仅影响相关的表现性任务?

**调研过程**:
- 分析了Google Docs, Notion等协作工具的"依赖更新"提示机制
- 研究了React状态管理中的"选择性re-render"模式
- 参考了Excel中公式依赖图的计算逻辑

**Decision**: 采用**粗粒度联动+用户确认**
- **变更检测粒度**: 模块级(Stage1变更→提示重新生成Stage2和Stage3)
- **重生成粒度**: 全量重生成(不做细粒度依赖追踪)
- **用户控制**: 弹窗询问"检测到阶段一的变更,是否重新生成评估设计和学习蓝图?",提供"仅重生成Stage2"/"重生成Stage2+3"/"稍后手动"三个选项

**Rationale**:
- **粗粒度简化实现**: 避免复杂的依赖图维护(符合Simplicity原则)
- **全量重生成保证一致性**: Agent间有隐含依赖(如Stage3的活动安排依赖Stage2的任务时间点),部分更新易导致不一致
- **用户确认保留控制权**: 教师可能只想微调Stage1而不影响已精心调整的Stage3,强制重生成会丢失工作成果

**Alternatives Considered**:
- ❌ 细粒度依赖追踪(如某个U→特定的表现性任务): 实现复杂,Agent prompt难以精确控制输出映射,维护成本高
- ❌ 自动静默重生成: 用户失去控制,可能丢失手动调整
- ❌ 不提供联动,完全手动: 违反FR要求,用户体验差

**Implementation Note**:
- 后端: `backend/app/services/workflow_service.py::detect_upstream_changes()`
  - 返回`{stage1_changed: bool, stage2_changed: bool, affected_stages: [2,3]}`
- 前端: `ChangeDetectionDialog.tsx`在进入Stage2/3时检查并弹窗
- 数据模型: `CourseProject.stage_versions`字段记录每个阶段的修改时间戳,用于比对

---

### 5. 导出Markdown的格式增强与工具兼容性

**Research Question**: 生成的Markdown应该针对哪些工具优化?(Typora, Notion, GitHub, 还是通用Markdown?)

**调研过程**:
- 测试了Typora, Notion, Obsidian, GitHub对CommonMark规范的支持差异
- 研究了Pandoc等转换工具对Markdown扩展语法的支持
- 参考了Markdown Best Practices(markdownguide.org)

**Decision**: 采用**严格CommonMark + 最小扩展**
- **基础格式**: 遵循CommonMark规范(GFM风格)
  - 标题使用ATX风格(#而非Setext)
  - 列表缩进使用空格(不用tab)
  - 代码块使用三个反引号(```)
- **扩展语法**(仅当必要):
  - 表格(GFM tables)用于评估量规(Rubric)
  - 任务列表(- [ ])用于活动清单(可选,P3优先级)
- **元数据**: YAML front matter(可选,用于Obsidian/Pandoc兼容)
- **图片**: 不内嵌,使用相对路径引用(如`![](images/rubric.png)`)

**Rationale**:
- CommonMark最广泛支持,Typora/Notion/GitHub均兼容
- 避免过度依赖特定工具的私有语法(如Notion callout blocks)
- 表格是Rubric展示的最佳格式,GFM tables足够简单且广泛支持

**Alternatives Considered**:
- ❌ 使用Notion blocks API直接导出: 锁定用户到Notion生态,违背开放性
- ❌ 纯HTML: 可读性差,不适合教师直接编辑
- ❌ PDF only: 不可编辑,限制二次调整

**Implementation Note**:
- 后端: `backend/app/services/export_service.py::generate_markdown()`
  - 使用Jinja2模板引擎渲染`docs/UBD教案模板.md`
  - 表格生成使用`tabulate` library(Markdown output format)
- 模板变量: `{course_name, design_principle, stage_one, stage_two, stage_three, ...}`

---

### 6. 性能优化策略:并发Agent调用 vs 流式响应

**Research Question**: 如何在<90秒内完成三Agent workflow且提供良好UX?

**调研过程**:
- 测试了当前三Agent的串行调用耗时(Agent1: 25s, Agent2: 30s, Agent3: 35s, 总计90s)
- 研究了FastAPI的StreamingResponse和Server-Sent Events(SSE)
- 参考了OpenAI ChatGPT的流式响应UX

**Decision**: 采用**串行执行+流式进度反馈**
- **执行模式**: 保持串行(Agent1→Agent2→Agent3),不做并发
  - 原因: Agent2依赖Agent1输出,Agent3依赖Agent2输出,无法真正并发
- **UX优化**: 使用Server-Sent Events(SSE)实时推送进度
  - 事件类型: `agent_start`, `agent_progress`, `agent_complete`, `workflow_complete`
  - 前端显示进度条和当前阶段(如"正在生成评估框架(2/3)...预计剩余40秒")
- **超时处理**: 单Agent超时阈值45秒,总workflow超时120秒(留buffer)

**Rationale**:
- 串行是必然,优化重点在感知性能而非实际性能
- SSE标准协议,FastAPI和React都有成熟库支持
- 进度条和时间预估显著改善用户等待体验(符合FR-032要求)

**Alternatives Considered**:
- ❌ 并发调用Agent2和Agent3: 逻辑上不可行,Agent3需要Agent2的表现性任务
- ❌ WebSocket双向通信: 过于复杂,SSE足够(仅需server→client推送)
- ❌ 轮询进度API: 低效且增加服务器负载

**Implementation Note**:
- 后端: `backend/app/api/v1/generate.py::stream_workflow()`
  - 使用`fastapi.responses.StreamingResponse`
  - Yield格式: `data: {"type": "agent_progress", "agent": "stage_two", "percent": 60}\n\n`
- 前端: `frontend-x/src/hooks/useStepWorkflow.ts`
  - 使用`EventSource` API监听SSE
  - 更新Zustand store中的`workflowProgress`状态

---

### 7. 测试策略:黄金标准案例的版本管理

**Research Question**: 当升级到V3后,V1/V2的黄金标准案例如何复用和更新?

**调研过程**:
- 研究了软件测试中的Snapshot Testing(如Jest snapshots)
- 分析了语义相似度计算方法(cosine similarity, ROUGE score)
- 参考了OpenAI Evals框架的评估方法

**Decision**: 采用**多版本golden standards + 语义匹配**
- **案例版本化**:
  - `backend/app/tests/golden_standards/v1/ai_programming_course.json` (保留)
  - `backend/app/tests/golden_standards/v2/ai_programming_course.json` (保留)
  - `backend/app/tests/golden_standards/v3/ai_programming_course_expected.json` (新建)
- **测试模式**:
  - V3 Agent输出与V3 expected比对(主要测试)
  - V3 Agent输出与V1/V2比对(回归测试,允许<80%相似度,确保核心逻辑未破坏)
- **相似度计算**: 使用sentence-transformers库计算embedding cosine similarity

**Rationale**:
- 多版本保留便于回归测试和问题定位
- 语义匹配比字符串精确匹配更合理(AI输出有随机性)
- ≥80%相似度阈值平衡严格性和灵活性

**Alternatives Considered**:
- ❌ 只保留V3案例: 无法检测升级引入的regression
- ❌ 字符串精确匹配: AI输出不稳定,会导致误报
- ❌ 人工评审每次输出: 不可扩展,无法CI/CD集成

**Implementation Note**:
- 后端测试: `backend/app/tests/test_agents/test_golden_standard_v3.py`
  - 使用`sentence-transformers/all-MiniLM-L6-v2`模型计算相似度
  - 断言: `assert similarity >= 0.80, f"Output similarity {similarity} below threshold"`
- CI集成: 在GitHub Actions中运行,失败时阻止merge

---

### 8. 前端架构重构：ChatGPT风格对话式UI vs tldraw无限画布

**Research Question**: 采用何种前端架构能更好地支持AI驱动的课程设计workflow？

**调研过程**:
- 分析了tldraw无限画布架构的优劣势（自由布局 vs 学习曲线陡峭）
- 研究了ChatGPT、Claude、Cursor等现代AI应用的对话式交互模式
- 评估了Ant Design X组件库对AI对话场景的支持
- 参考了线性步骤引导（Wizard）与对话式生成的结合案例

**Decision**: 采用**ChatGPT风格对话式UI + 步骤引导 + 分栏预览/编辑**

**核心设计**:

1. **顶部步骤导航**:
   ```
   [1.锚定理解✓] → [2.评估证据🔄] → [3.学习蓝图⏸] → [4.完整方案⏸]
   ```
   - 状态：✓已完成, 🔄进行中, ⏸未开始
   - 串行流程：必须完成步骤N才能进入步骤N+1
   - 完成标准：AI生成内容后自动标记为完成

2. **主工作区分栏布局**:
   - **左侧(40%)**: 对话窗口 (ChatGPT风格)
     - 显示用户与AI的对话历史
     - 用户可通过对话修改内容（如"第二个U太具体了"）
     - AI理解意图后直接修改右侧Markdown，并在对话中确认
   - **右侧(60%)**: 内容预览/编辑区
     - 默认：预览模式（渲染后的Markdown）
     - 点击"编辑"：切换为Markdown文本编辑器
     - 实时保存用户修改

3. **交互流程**:
   - **步骤进入**：用户点击步骤N → 自动触发AI生成 → 流式输出到右侧
   - **对话修改**：用户在左侧对话框输入 → AI理解意图 → 直接修改右侧内容 → 对话中确认"已将第二个U修改为..."
   - **直接编辑**：用户点击"编辑" → Markdown文本编辑器 → 保存后更新数据库和对话历史
   - **下一步**：AI生成完成后，"下一步"按钮自动激活 → 用户点击进入下一阶段

4. **步骤间依赖展示**:
   - 进入步骤2时显示："正在基于步骤1的3个U、2个Q生成驱动性问题..."
   - 对话框顶部固定显示当前依赖的前序步骤内容摘要

5. **Markdown文件管理**:
   - 每个步骤生成独立文件：`stage1.md`, `stage2.md`, `stage3.md`
   - 步骤4"完整方案"：自动合并所有阶段文件，添加目录和引言
   - 用户可下载完整方案（单一Markdown文件）

**技术选型**:

- **UI框架**: Ant Design X (专为AI应用场景设计)
  - 核心组件:
    - `<Conversations>` + `<Bubble>` - 对话气泡展示
    - `<Sender>` - 消息发送框（支持多模态输入）
    - `<Prompts>` - 智能提示词建议
    - `useXAgent` / `useXChat` - AI对话管理hooks

- **Markdown处理**:
  - 编辑：CodeMirror 6 (轻量，语法高亮)
  - 预览：react-markdown + remark-gfm (支持GFM tables)

- **步骤管理**:
  - Ant Design `<Steps>` 组件（顶部导航）
  - Zustand store管理当前步骤状态和完成标记

- **状态管理**:
  ```typescript
  interface CourseState {
    currentStep: 1 | 2 | 3 | 4;
    stepStatus: Record<number, 'pending' | 'generating' | 'completed'>;
    conversationHistory: Record<number, Message[]>; // 每个步骤独立对话历史
    stageMarkdowns: Record<number, string>; // stage1.md, stage2.md, stage3.md
    isEditMode: boolean; // 右侧预览/编辑模式切换
  }
  ```

**Rationale**:

- ✅ **降低学习成本**: ChatGPT风格的对话界面已成为AI应用标准，用户无需学习
- ✅ **更好的AI交互**: 对话式修改比传统表单填写更自然，符合AI时代的交互范式
- ✅ **清晰的流程指引**: 步骤导航明确展示UbD三阶段逻辑，避免用户迷失
- ✅ **灵活的内容编辑**: 预览/编辑模式切换满足不同用户偏好（对话 vs 直接修改）
- ✅ **完整的对话上下文**: 保存对话历史便于用户回溯设计思路，也为后续AI优化提供数据

**Alternatives Considered**:

- ❌ **保留tldraw无限画布**:
  - 优点：自由布局，可视化关系
  - 缺点：学习曲线陡峭，不符合AI对话交互范式，维护成本高
  - 拒绝原因：过度设计，不符合Simplicity原则

- ❌ **纯表单式界面**:
  - 优点：传统，开发简单
  - 缺点：无法发挥AI对话能力，用户体验差
  - 拒绝原因：浪费AI交互优势

- ❌ **完全对话式（无右侧预览）**:
  - 优点：极简
  - 缺点：用户无法快速预览完整内容，编辑困难
  - 拒绝原因：对教案这种长文档不适用

**Implementation Note**:

- 前端项目重命名：`frontend-v2` → `frontend-x` (基于Ant Design X)
- 核心文件结构：
  ```
  frontend-x/
  ├── src/
  │   ├── components/
  │   │   ├── StepNavigator.tsx         # 顶部步骤导航
  │   │   ├── ChatPanel.tsx             # 左侧对话面板（基于Ant Design X）
  │   │   ├── ContentPanel.tsx          # 右侧内容面板
  │   │   ├── MarkdownPreview.tsx       # Markdown预览模式
  │   │   ├── MarkdownEditor.tsx        # Markdown编辑模式
  │   │   └── DownloadButton.tsx        # 下载完整方案按钮
  │   ├── hooks/
  │   │   ├── useStepWorkflow.ts        # 步骤流程管理
  │   │   ├── useChatConversation.ts    # 对话管理（基于useXChat）
  │   │   └── useMarkdownSync.ts        # Markdown同步到后端
  │   ├── stores/
  │   │   └── courseStore.ts            # Zustand状态（包含conversationHistory）
  │   └── constants/
  │       └── ubdDefinitions.ts         # UbD定义（对话中可引用）
  ```

- 对话历史持久化：
  - 每次用户发送消息或AI回复后，立即POST到后端保存
  - API: `POST /api/v1/courses/{id}/conversation` (新增endpoint)

- 步骤间依赖提示：
  - AI生成步骤2时，系统消息自动插入："正在基于步骤1的内容生成评估设计..."
  - 提示内容由后端workflow_service生成，包含具体的U/Q数量

---

## Summary of Decisions

| Area | Decision | Impact |
|------|----------|--------|
| UX帮助系统 | 分层帮助(卡片说明+浮层+onboarding) | 新增3个前端组件, ubdDefinitions.ts常量文件 |
| UbD验证 | 规则层+语义层两层验证 | 新增validation_service.py, ubd_rules.yaml |
| PBL阶段 | 4个预设阶段+有限自定义 | LearningActivity.phase_type enum, 前端4折叠面板 |
| 编辑联动 | 粗粒度模块级+用户确认 | workflow_service.detect_upstream_changes(), ChangeDetectionDialog |
| Markdown导出 | 严格CommonMark + GFM tables | Jinja2模板, tabulate库 |
| 性能优化 | 串行执行+SSE流式进度 | StreamingResponse endpoint, EventSource hook |
| 测试策略 | 多版本golden standards + 语义匹配 | sentence-transformers库, v3测试案例 |

## Action Items for Phase 1

根据研究结果,Phase 1需要:

1. **数据模型扩展**:
   - `LearningActivity.phase_type: Enum['launch', 'build', 'develop', 'present']`
   - `CourseProject.stage_versions: JSON{stage1_modified: timestamp, ...}`
   - `StageData`添加ubd_labels, whereto_labels字段

2. **新建文件**:
   - `backend/app/services/validation_service.py`
   - `backend/app/config/ubd_rules.yaml`
   - `frontend-x/src/components/TooltipHelper.tsx`
   - `frontend-x/src/components/HelpDialog.tsx`
   - `frontend-x/src/components/OnboardingOverlay.tsx`
   - `frontend-x/src/components/ChangeDetectionDialog.tsx`
   - `frontend-x/src/constants/ubdDefinitions.ts`
   - `frontend-x/src/hooks/useStepWorkflow.ts`

3. **PHR文件创建**:
   - `backend/app/prompts/phr/project_foundation_v2.md`
   - `backend/app/prompts/phr/assessment_framework_v2.md`
   - `backend/app/prompts/phr/learning_blueprint_v2.md`

4. **API合约设计**:
   - `POST /api/v1/workflow/stream` - SSE endpoint
   - `POST /api/v1/validate/ubd-element` - UbD验证endpoint
   - `GET /api/v1/course/{id}/changes` - 变更检测endpoint
   - 扩展现有的`PUT /api/v1/course/{id}/stage/{stage_num}` - 支持编辑

5. **测试案例**:
   - `backend/app/tests/golden_standards/v3/ai_programming_course_expected.json`
   - 更新现有Agent测试以使用PHR v2

所有NEEDS CLARIFICATION项已解决,可进入Phase 1设计阶段。
