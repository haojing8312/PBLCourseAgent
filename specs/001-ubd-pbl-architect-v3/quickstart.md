# Quickstart Guide: UbD-PBL 课程架构师 V3

**Feature**: UbD-PBL 课程架构师 V3
**Last Updated**: 2025-10-20

## Purpose

This guide helps developers quickly understand and start implementing the UbD-PBL Course Architect V3 feature. It provides step-by-step setup, development workflow, and key implementation notes.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- uv (Python package manager)
- Modern browser (Chrome/Firefox/Safari/Edge)

## 5-Minute Overview

**What is UbD-PBL V3?**
Upgrades the existing PBL course generator to a professional UbD-PBL Course Architect by:
1. Embedding UbD theory in UI (explanation tooltips on G/U/Q/K/S cards)
2. Enhancing AI Agents to generate UbD-aligned content (U is abstract ideas, not knowledge points)
3. Restructuring learning blueprints into 4 PBL phases (Launch → Build → Develop → Present)
4. Enabling user editing with cascade regeneration detection
5. Improving Markdown export with theory explanations

**Tech Stack**:
- Backend: Python 3.10 + FastAPI + SQLAlchemy + OpenAI SDK
- Frontend: React 18 + TypeScript + Ant Design X + Zustand + CodeMirror 6 + react-markdown
- Database: SQLite (MVP)
- Testing: pytest (backend), Vitest (frontend), Golden Standards

---

## Quick Setup

### 1. Clone and Enter Project

```bash
git checkout 001-ubd-pbl-architect-v3
cd eduagents
```

### 2. Backend Setup

```bash
cd backend

# Initialize uv environment
uv sync

# Create .env file
cp .env.example .env
# Edit .env and set PBL_AI_API_KEY=your_key

# Run database migrations (when created)
uv run alembic upgrade head

# Start backend server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 48097
```

Backend will be available at `http://localhost:48097`

### 3. Frontend Setup

```bash
cd frontend-x

# Install dependencies (including Ant Design X)
npm install

# Start dev server
npm run dev
```

Frontend will be available at `http://localhost:48098`

### 4. Verify Setup

Open browser at `http://localhost:3000` and:
1. Create a new course project
2. Enter title "Test Course"
3. Click "Generate" to run the 3-stage workflow
4. Verify SSE progress display works
5. Check generated G/U/Q/K/S in Stage One

---

## Development Workflow

### Phase 1: Backend Agent Upgrade

**Goal**: Create PHR v2 prompts and upgrade Agent classes

**Steps**:

1. **Create PHR v2 Files** (Prompt History Records)
   ```bash
   cd backend/app/prompts/phr

   # Copy v1 templates as starting point
   cp project_foundation_v1.md project_foundation_v2.md
   cp assessment_framework_v1.md assessment_framework_v2.md
   cp learning_blueprint_v1.md learning_blueprint_v2.md
   ```

2. **Update PHR v2 Content** (see research.md for requirements)
   - `project_foundation_v2.md`:
     - Emphasize U must be abstract ideas (not knowledge points)
     - Add explicit validation instructions for U vs K
   - `assessment_framework_v2.md`:
     - Driving question must have real context + deliverable
     - Performance tasks must include PBL attributes
   - `learning_blueprint_v2.md`:
     - Organize by 4 PBL phases (not linear days)
     - Add UbD labels + WHERETO labels to each activity

3. **Upgrade Agent Classes**
   ```python
   # backend/app/agents/project_foundation.py

   def _build_system_prompt(self) -> str:
       """
       Prompt版本: 参见 backend/app/prompts/phr/project_foundation_v2.md
       """
       # Load from PHR v2 file
       with open('backend/app/prompts/phr/project_foundation_v2.md') as f:
           phr_content = f.read()
       # Extract system prompt section
       return extract_system_prompt(phr_content)
   ```

4. **Run Tests**
   ```bash
   uv run pytest app/tests/test_agents/ -v
   # Verify v2 outputs meet requirements
   ```

### Phase 2: Backend Data Model & API

**Goal**: Implement new database schema and API endpoints

**Steps**:

1. **Create SQLAlchemy Models** (see data-model.md)
   ```python
   # backend/app/models/course_project.py

   class CourseProject(Base):
       __tablename__ = "course_projects"
       id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
       title = Column(String(200), nullable=False)
       stage_versions = Column(JSON, default=dict)
       # ... other fields

   # backend/app/models/stage_data.py
   # Similar for StageOneData, StageTwoData, StageThreeData
   ```

2. **Create Database Migration**
   ```bash
   uv run alembic revision --autogenerate -m "Add V3 schema"
   uv run alembic upgrade head
   ```

3. **Implement API Endpoints** (see contracts/openapi.yaml)
   ```python
   # backend/app/api/v1/course.py

   @router.put("/courses/{course_id}/stage-one")
   async def update_stage_one(course_id: str, data: UpdateStageOneRequest):
       # 1. Update StageOneData
       # 2. Run UbD validation
       # 3. Update stage_versions timestamp
       # 4. Return updated data + warnings
       pass
   ```

4. **Implement SSE Workflow**
   ```python
   # backend/app/api/v1/generate.py

   from fastapi.responses import StreamingResponse

   @router.post("/workflow/stream")
   async def stream_workflow(course_id: str):
       async def event_generator():
           yield "data: {\"type\": \"agent_start\", \"agent\": \"stage_one\"}\n\n"
           # Run Agent 1
           result1 = await project_foundation_agent.generate(...)
           yield f"data: {{\"type\": \"agent_complete\", \"agent\": \"stage_one\", \"result\": {result1}}}\n\n"
           # ... Agent 2, Agent 3

       return StreamingResponse(event_generator(), media_type="text/event-stream")
   ```

5. **Implement Validation Service** (research.md #2)
   ```python
   # backend/app/services/validation_service.py

   def validate_understanding_vs_knowledge(text: str) -> ValidationResult:
       # Rule layer: keyword blacklist
       if any(keyword in text for keyword in ['掌握', '学会', '会使用']):
           return ValidationResult(is_valid=False, confidence=0.2, warnings=[...])

       # Semantic layer: AI classification
       prompt = f"判断以下陈述是'抽象的持续理解'还是'具体的知识点': {text}"
       response = openai_client.chat.completions.create(...)
       # Parse and return
   ```

6. **Test API**
   ```bash
   uv run pytest app/tests/test_api/ -v
   ```

### Phase 3: ChatGPT-Style Frontend Implementation

**Goal**: Build conversational UI with Ant Design X components, step navigation, and split-panel layout

**Steps**:

1. **Create UbD Definitions**
   ```typescript
   // frontend-x/src/constants/ubdDefinitions.ts

   export const UBD_DEFINITIONS = {
     G: {
       title: "迁移目标 (Transfer Goals)",
       shortHelp: "学生将能够自主地将所学应用到......",
       detailedHelp: "迁移目标描述学生在没有教师指导的情况下,能够将知识和技能应用到新情境中的能力。",
       examples: {
         good: ["独立设计AI解决方案来解决真实社区问题"],
         bad: ["记住Python语法规则"]
       }
     },
     U: {
       title: "持续理解 (Enduring Understandings)",
       shortHelp: "学生在忘记所有细节后,我们希望他们能永恒记住的核心思想或重要观点是什么?",
       detailedHelp: "持续理解是抽象的、可迁移的big ideas,而不是具体的知识点或技能。",
       examples: {
         good: ["理解AI技术的双刃剑特性"],
         bad: ["掌握Python编程语法"]
       }
     },
     // ... Q, K, S
   };
   ```

2. **Implement Step Navigator**
   ```tsx
   // frontend-x/src/components/StepNavigator.tsx
   import { Steps } from 'antd';

   export const StepNavigator: React.FC = () => {
     const {currentStep, stepStatus} = useCourseStore();

     const items = [
       {title: '1. 锚定理解', status: stepStatus[1]},
       {title: '2. 评估证据', status: stepStatus[2]},
       {title: '3. 学习蓝图', status: stepStatus[3]},
       {title: '4. 完整方案', status: stepStatus[4]}
     ];

     return (
       <Steps
         current={currentStep - 1}
         items={items.map((item, idx) => ({
           title: item.title,
           status: item.status === 'completed' ? 'finish' :
                   item.status === 'generating' ? 'process' : 'wait',
           disabled: idx > currentStep
         }))}
       />
     );
   };
   ```

3. **Build Chat Panel with Ant Design X**
   ```tsx
   // frontend-x/src/components/ChatPanel.tsx
   import { Conversations, Bubble, Sender, Prompts, useXChat } from '@ant-design/x';

   export const ChatPanel: React.FC = () => {
     const {currentStep} = useCourseStore();
     const {messages, sendMessage} = useChatConversation(currentStep);

     return (
       <div className="chat-panel" style={{width: '40%', borderRight: '1px solid #eee'}}>
         <Conversations
           items={messages}
           renderMessage={(msg) => (
             <Bubble
               variant={msg.role === 'user' ? 'shadow' : 'outlined'}
               content={msg.content}
               avatar={msg.role === 'assistant' ? '/ai-avatar.png' : undefined}
             />
           )}
         />
         <Sender
           placeholder="输入您的修改要求..."
           onSubmit={(text) => sendMessage(text)}
         />
         <Prompts
           items={[
             {label: '修改为更抽象的表述', key: 'abstract'},
             {label: '增加一个理解目标', key: 'add-u'}
           ]}
           onSelect={(item) => sendMessage(item.label)}
         />
       </div>
     );
   };
   ```

4. **Build Content Panel with Preview/Edit Modes**
   ```tsx
   // frontend-x/src/components/ContentPanel.tsx
   import { Button, Space } from 'antd';

   export const ContentPanel: React.FC = () => {
     const {currentStep, stageMarkdowns, isEditMode, setEditMode} = useCourseStore();
     const markdown = stageMarkdowns[currentStep] || '';

     return (
       <div className="content-panel" style={{width: '60%', padding: 24}}>
         <Space style={{marginBottom: 16}}>
           <Button type={!isEditMode ? 'primary' : 'default'} onClick={() => setEditMode(false)}>
             预览
           </Button>
           <Button type={isEditMode ? 'primary' : 'default'} onClick={() => setEditMode(true)}>
             编辑
           </Button>
         </Space>

         {isEditMode ? (
           <MarkdownEditor value={markdown} onChange={(val) => updateMarkdown(currentStep, val)} />
         ) : (
           <MarkdownPreview markdown={markdown} />
         )}
       </div>
     );
   };
   ```

5. **Implement Chat Conversation Hook**
   ```typescript
   // frontend-x/src/hooks/useChatConversation.ts
   import { useXChat } from '@ant-design/x';

   export const useChatConversation = (step: number) => {
     const [messages, setMessages] = useState<Message[]>([]);
     const {courseId} = useCourseStore();

     // Load history on mount
     useEffect(() => {
       loadConversationHistory(courseId, step).then(setMessages);
     }, [courseId, step]);

     const sendMessage = useCallback(async (content: string) => {
       const userMsg = {role: 'user', content, timestamp: new Date().toISOString()};

       // Save to backend
       await saveConversation(courseId, step, userMsg);
       setMessages(prev => [...prev, userMsg]);

       // Send to AI and stream response
       const eventSource = new EventSource(
         `/api/v1/workflow/stream?courseId=${courseId}&step=${step}&userInput=${encodeURIComponent(content)}`
       );

       eventSource.onmessage = (event) => {
         const data = JSON.parse(event.data);
         if (data.type === 'agent_complete') {
           const aiMsg = {role: 'assistant', content: data.result.message, timestamp: new Date().toISOString()};
           saveConversation(courseId, step, aiMsg);
           setMessages(prev => [...prev, aiMsg]);
           eventSource.close();
         }
       };
     }, [courseId, step]);

     return {messages, sendMessage};
   };
   ```

6. **Implement Step Workflow Control**
   ```typescript
   // frontend-x/src/hooks/useStepWorkflow.ts

   export const useStepWorkflow = () => {
     const {currentStep, stepStatus, setStepStatus, setCurrentStep} = useCourseStore();

     const canProceedToStep = (targetStep: number) => {
       // Must complete previous step
       return stepStatus[targetStep - 1] === 'completed';
     };

     const completeCurrentStep = () => {
       setStepStatus(currentStep, 'completed');
     };

     const moveToNextStep = () => {
       if (canProceedToStep(currentStep + 1)) {
         setCurrentStep(currentStep + 1);
         setStepStatus(currentStep + 1, 'generating');
         // Auto-trigger AI generation for new step
         triggerStepGeneration(currentStep + 1);
       }
     };

     return {canProceedToStep, completeCurrentStep, moveToNextStep};
   };
   ```

7. **Test Frontend**
   ```bash
   npm run test
   npm run lint
   ```

### Phase 4: Golden Standard Testing

**Goal**: Ensure AI outputs meet quality standards

**Steps**:

1. **Create V3 Golden Standard**
   ```json
   // backend/app/tests/golden_standards/v3/ai_programming_course_expected.json

   {
     "course_title": "0基础AI编程课程",
     "stage_one": {
       "understandings": [
         "理解AI技术的双刃剑特性: 既能带来便利也可能造成风险",
         "认识到技术伦理需要在开发和应用的每个阶段考虑"
       ],
       "knowledge": [
         "AI的基本概念和分类(机器学习、深度学习、NLP等)",
         "Python编程基础语法"
       ]
       // ... NOT "掌握Python语法" in U
     },
     "stage_two": {
       "driving_question": "我们如何利用AI技术,为我们的社区创造一个有价值的解决方案?",
       "performance_tasks": [
         {
           "title": "社区问题调研报告",
           "context": "作为社区研究员,你需要识别社区中可能通过AI技术改善的实际问题...",
           "deliverable": "5页调研报告 + 3分钟汇报",
           "milestone_week": 3
         }
       ]
     },
     "stage_three": {
       "phases": [
         {
           "type": "launch",
           "activities": [
             {
               "title": "专家讲座: AI在社区中的应用",
               "ubd_labels": ["U1", "Q1"],
               "whereto_labels": ["H-Hook"]
             }
           ]
         }
         // ... build, develop, present phases
       ]
     }
   }
   ```

2. **Implement Semantic Similarity Test**
   ```python
   # backend/app/tests/test_agents/test_golden_standard_v3.py

   from sentence_transformers import SentenceTransformer
   import pytest

   model = SentenceTransformer('all-MiniLM-L6-v2')

   def test_stage_one_understandings_quality():
       # Generate with Agent V2
       result = project_foundation_agent.generate(input_data)

       # Load golden standard
       with open('backend/app/tests/golden_standards/v3/ai_programming_course_expected.json') as f:
           expected = json.load(f)

       # Compute semantic similarity
       generated_us = [u['text'] for u in result['understandings']]
       expected_us = expected['stage_one']['understandings']

       embeddings_gen = model.encode(generated_us)
       embeddings_exp = model.encode(expected_us)

       similarity = cosine_similarity(embeddings_gen, embeddings_exp).mean()

       assert similarity >= 0.80, f"Similarity {similarity} below threshold"
   ```

3. **Run All Tests**
   ```bash
   uv run pytest app/tests/ -v --tb=short
   ```

---

## Key Files to Modify

### Backend

**Existing Files to Upgrade**:
- `backend/app/agents/project_foundation.py` → Reference PHR v2
- `backend/app/agents/assessment_framework.py` → Reference PHR v2
- `backend/app/agents/learning_blueprint.py` → Reference PHR v2
- `backend/app/api/v1/course.py` → Add edit endpoints
- `backend/app/api/v1/generate.py` → Add SSE endpoint
- `backend/app/services/workflow_service.py` → Add change detection
- `backend/app/services/export_service.py` → Update Markdown template

**New Files to Create**:
- `backend/app/prompts/phr/project_foundation_v2.md`
- `backend/app/prompts/phr/assessment_framework_v2.md`
- `backend/app/prompts/phr/learning_blueprint_v2.md`
- `backend/app/models/learning_activity.py` (if making separate table)
- `backend/app/services/validation_service.py`
- `backend/app/config/ubd_rules.yaml`
- `backend/app/tests/golden_standards/v3/ai_programming_course_expected.json`

### Frontend

**注意**: 前端完全重构为ChatGPT风格对话式UI,所有组件从零开始创建。

**核心新文件**:
- `frontend-x/src/components/StepNavigator.tsx` → 顶部步骤导航
- `frontend-x/src/components/ChatPanel.tsx` → 左侧对话面板(使用Ant Design X)
- `frontend-x/src/components/ContentPanel.tsx` → 右侧内容面板
- `frontend-x/src/components/MarkdownPreview.tsx` → Markdown预览组件
- `frontend-x/src/components/MarkdownEditor.tsx` → Markdown编辑组件(CodeMirror 6)
- `frontend-x/src/components/DownloadButton.tsx` → 下载按钮组件
- `frontend-x/src/components/UbdTooltip.tsx` → UbD理论tooltip

**核心Hooks**:
- `frontend-x/src/hooks/useStepWorkflow.ts` → 步骤流程控制
- `frontend-x/src/hooks/useChatConversation.ts` → 对话管理(集成Ant Design X useXChat)
- `frontend-x/src/hooks/useMarkdownSync.ts` → Markdown实时同步

**服务层**:
- `frontend-x/src/services/workflowService.ts` → SSE流式API调用
- `frontend-x/src/services/conversationService.ts` → 对话历史CRUD
- `frontend-x/src/services/exportService.ts` → 导出下载

**状态管理**:
- `frontend-x/src/stores/courseStore.ts` → Zustand状态(currentStep, stepStatus, conversationHistory, stageMarkdowns, isEditMode)

**常量和类型**:
- `frontend-x/src/constants/ubdDefinitions.ts` → UbD理论定义
- `frontend-x/src/types/course.ts` → 课程数据类型
- `frontend-x/src/types/conversation.ts` → 对话消息类型

---

## Testing Checklist

### Backend Tests

- [ ] Agent v2 Prompt tests (pytest)
- [ ] API endpoint tests (pytest + testclient)
- [ ] Golden standard v3 comparison (semantic similarity ≥80%)
- [ ] UbD validation service tests (U vs K, Q format, etc.)
- [ ] SSE stream tests (event sequence correctness)
- [ ] Change detection tests (timestamp comparison)
- [ ] Database migration tests (v2 to v3)

### Frontend Tests

- [ ] StepNavigator显示正确的步骤状态 (Vitest + React Testing Library)
- [ ] ChatPanel集成Ant Design X Conversations组件 (Vitest)
- [ ] ContentPanel预览/编辑模式切换 (Vitest)
- [ ] useChatConversation hook正确保存和加载对话历史 (Vitest)
- [ ] useStepWorkflow正确控制步骤进入条件 (Vitest)
- [ ] SSE流式消息正确更新对话窗口 (integration test)
- [ ] Markdown编辑器实时保存到后端 (integration test)
- [ ] 依赖提示正确显示(如"正在基于步骤1的3个U生成...") (snapshot test)
- [ ] 完整方案下载功能 (E2E test)

### Integration Tests

- [ ] Full workflow: Create → Generate → Edit → Regenerate → Export
- [ ] User Story 1 acceptance scenarios (all 6 scenarios)
- [ ] User Story 2 acceptance scenarios (UbD learning)
- [ ] User Story 3 acceptance scenarios (editing + cascade)
- [ ] Edge cases (AI failure, concurrent edits, empty states)

---

## Common Issues & Solutions

### Issue 1: AI Generation Returns Knowledge Points in U

**Symptom**: `"掌握Python编程语法"` appears in Understandings

**Solution**:
1. Check PHR v2 prompt has explicit U vs K differentiation instructions
2. Verify validation_service is catching this in post-generation validation
3. If validation score < 0.7, show warning in frontend
4. Update PHR v2 with negative examples

### Issue 2: SSE Stream Stops Mid-Workflow

**Symptom**: EventSource closes unexpectedly after Agent 1

**Solution**:
1. Check backend logs for exceptions
2. Verify timeout settings (default 120s may be too short)
3. Add try-catch around each Agent call in stream generator
4. Implement heartbeat events (send empty comment every 10s to keep connection alive)

### Issue 3: Change Detection Always Shows False

**Symptom**: Editing Stage One doesn't trigger regeneration prompt

**Solution**:
1. Verify `stage_versions` JSON is being updated on PUT
2. Check timezone consistency (UTC vs local time)
3. Ensure frontend is calling `/changes` API before entering Stage Two
4. Add debug logging to `detect_upstream_changes()`

---

## Performance Optimization

### Backend

- Use FastAPI `BackgroundTasks` for async Agent execution
- Implement Redis caching for validation results
- Use connection pooling for database (SQLAlchemy async)
- Optimize Prompt length (reduce token count by 20% without quality loss)

### Frontend

- 懒加载步骤组件 (React.lazy + Suspense,每个步骤首次进入时加载)
- Debounce对话消息保存 (500ms延迟,减少API调用)
- 虚拟化长对话历史 (Ant Design X Conversations组件内置虚拟滚动)
- CodeMirror编辑器按需加载 (仅在编辑模式时加载)
- 使用react-markdown的轻量级配置 (禁用不需要的remark插件)

---

## Next Steps After Quickstart

1. **Read Design Docs**:
   - [Research](research.md) - Design decisions and alternatives
   - [Data Model](data-model.md) - Database schema details
   - [API Contracts](contracts/README.md) - Complete API reference

2. **Review Constitution**:
   - [Constitution](../../.specify/memory/constitution.md) - Project principles
   - Ensure all code follows Linus-style philosophy (good taste, simplicity)

3. **Run `/speckit.tasks`**:
   - Generate detailed task breakdown from this plan
   - Follow TDD workflow (test first, then implement)

4. **Submit for Review**:
   - Ensure all tests pass (`pytest` + `npm test`)
   - Run code quality checks (`black`, `eslint`)
   - Compare outputs against golden standards (≥80% similarity)

---

**Happy Coding!** 🚀

If you encounter issues, refer to:
- [Specification](spec.md) for requirements clarification
- [Plan](plan.md) for overall architecture
- [CLAUDE.md](../../CLAUDE.md) for development guidelines
