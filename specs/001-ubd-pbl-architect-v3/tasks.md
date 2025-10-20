# Tasks: UbD-PBL 课程架构师 V3

**Input**: Design documents from `/specs/001-ubd-pbl-architect-v3/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests will be implemented per quickstart.md checklist after core functionality

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/app/` (FastAPI + SQLAlchemy)
- **Frontend**: `frontend-x/src/` (React + TypeScript + Ant Design X)
- **PHR**: `backend/app/prompts/phr/` (Prompt History Records v2)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create PHR v2 prompt files from v1 templates in backend/app/prompts/phr/
- [x] T002 [P] Install frontend-x dependencies (npm create vite@latest + Ant Design X + CodeMirror 6 + react-markdown)
- [x] T003 [P] Configure backend development environment (uv sync + .env setup with PBL_AI_API_KEY)
- [x] T004 [P] Create golden standard V3 test case file in backend/app/tests/golden_standards/v3/ai_programming_course_expected.json
- [x] T005 [P] Setup frontend build tooling in frontend-x/vite.config.ts (Ant Design X optimization, CodeMirror bundle splitting)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create database migration for CourseProject.conversation_history field in backend/app/models/course_project.py
- [x] T007 [P] Create UbD definitions constants file in frontend-x/src/constants/ubdDefinitions.ts (G/U/Q/K/S explanations)
- [x] T008 [P] Implement validation_service.py for UbD element validation (U vs K semantic check) in backend/app/services/validation_service.py
- [x] T009 [P] Create base courseStore with Zustand in frontend-x/src/stores/courseStore.ts (currentStep, stepStatus, conversationHistory, stageMarkdowns, isEditMode)
- [x] T010 [P] Setup SSE workflow endpoint in backend/app/api/v1/generate.py (POST /api/v1/workflow/stream)
- [x] T011 [P] Implement conversation API endpoints in backend/app/api/v1/course.py (POST/GET /api/v1/courses/{id}/conversation)
- [x] T012 Create StepNavigator component in frontend-x/src/components/StepNavigator.tsx (Ant Design Steps)
- [x] T013 [P] Configure sentence-transformers for semantic similarity testing in backend/app/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 创建完整的UbD-PBL课程方案 (Priority: P1) 🎯 MVP

**Goal**: 教师通过三个AI辅助的阶段(锚定理解目标 → 设计评估证据 → 规划学习体验),最终生成一份结构完整、理论清晰、可直接使用的UbD-PBL课程方案

**Independent Test**: 输入课程主题"0基础AI编程课程",完整走完三个阶段,并导出符合模板要求的教案文档。交付的文档应包含G/U/Q/K/S、驱动性问题、表现性任务、评估量规和详细的PBL学习蓝图。

### Backend: Agent Prompt Upgrades (PHR v2)

- [ ] T014 [P] [US1] Create project_foundation_v2.md in backend/app/prompts/phr/ with enhanced U vs K differentiation instructions
- [ ] T015 [P] [US1] Create assessment_framework_v2.md in backend/app/prompts/phr/ with PBL driving question template
- [ ] T016 [P] [US1] Create learning_blueprint_v2.md in backend/app/prompts/phr/ with WHERETO principles and 4-phase PBL structure

### Backend: Agent Class Upgrades

- [ ] T017 [US1] Upgrade ProjectFoundationAgent._build_system_prompt() to load PHR v2 in backend/app/agents/project_foundation.py
- [ ] T018 [US1] Upgrade AssessmentFrameworkAgent._build_system_prompt() to load PHR v2 in backend/app/agents/assessment_framework.py
- [ ] T019 [US1] Upgrade LearningBlueprintAgent._build_system_prompt() to load PHR v2 in backend/app/agents/learning_blueprint.py

### Backend: Data Models

- [ ] T020 [P] [US1] Update StageOneData model to include validation_score in understandings JSON in backend/app/models/stage_data.py
- [ ] T021 [P] [US1] Update StageTwoData model schema in backend/app/models/stage_data.py
- [ ] T022 [P] [US1] Create PerformanceTask model in backend/app/models/performance_task.py
- [ ] T023 [P] [US1] Create Rubric model in backend/app/models/rubric.py
- [ ] T024 [P] [US1] Update StageThreeData model to include whereto_labels in activities JSON in backend/app/models/stage_data.py

### Backend: Workflow Service

- [ ] T025 [US1] Implement SSE stream generator in workflow_service.py (stream stage1→2→3 with progress events) in backend/app/services/workflow_service.py
- [ ] T026 [US1] Add post-generation UbD validation call to validation_service in backend/app/services/workflow_service.py
- [ ] T027 [US1] Implement change detection logic (stage_versions timestamp comparison) in backend/app/services/workflow_service.py

### Backend: Export Service

- [ ] T028 [US1] Create updated Markdown template with UbD theory explanations in backend/app/templates/course_export_v3.md.jinja2
- [ ] T029 [US1] Update export_service.py to use new template and generate full UbD-PBL plan in backend/app/services/export_service.py

### Frontend: ChatGPT-Style UI Components

- [ ] T030 [P] [US1] Create ChatPanel component with Ant Design X <Conversations> in frontend-x/src/components/ChatPanel.tsx
- [ ] T031 [P] [US1] Create ContentPanel component with preview/edit toggle in frontend-x/src/components/ContentPanel.tsx
- [ ] T032 [P] [US1] Create MarkdownPreview component with react-markdown in frontend-x/src/components/MarkdownPreview.tsx
- [ ] T033 [P] [US1] Create MarkdownEditor component with CodeMirror 6 in frontend-x/src/components/MarkdownEditor.tsx
- [ ] T034 [P] [US1] Create UbdTooltip component for G/U/Q/K/S explanations in frontend-x/src/components/UbdTooltip.tsx
- [ ] T035 [P] [US1] Create DownloadButton component for final export in frontend-x/src/components/DownloadButton.tsx

### Frontend: Hooks

- [ ] T036 [P] [US1] Implement useStepWorkflow hook (step navigation control, serial flow enforcement) in frontend-x/src/hooks/useStepWorkflow.ts
- [ ] T037 [P] [US1] Implement useChatConversation hook (Ant Design X useXChat integration, SSE message streaming) in frontend-x/src/hooks/useChatConversation.ts
- [ ] T038 [P] [US1] Implement useMarkdownSync hook (debounced auto-save to backend) in frontend-x/src/hooks/useMarkdownSync.ts

### Frontend: Services

- [ ] T039 [P] [US1] Create workflowService.ts with SSE EventSource handling in frontend-x/src/services/workflowService.ts
- [ ] T040 [P] [US1] Create conversationService.ts with conversation CRUD APIs in frontend-x/src/services/conversationService.ts
- [ ] T041 [P] [US1] Create exportService.ts with download API in frontend-x/src/services/exportService.ts

### Frontend: Types

- [ ] T042 [P] [US1] Define course types in frontend-x/src/types/course.ts (CourseProject, StageData interfaces)
- [ ] T043 [P] [US1] Define conversation types in frontend-x/src/types/conversation.ts (Message, ConversationHistory interfaces)

### Frontend: Main App

- [ ] T044 [US1] Integrate all components into App.tsx with split-panel layout (StepNavigator + ChatPanel + ContentPanel) in frontend-x/src/App.tsx
- [ ] T045 [US1] Implement step 1 auto-generation trigger on course creation in frontend-x/src/App.tsx
- [ ] T046 [US1] Implement dependency display (e.g., "正在基于步骤1的3个U生成...") when entering step 2/3 in frontend-x/src/components/ChatPanel.tsx

### Integration & Validation

- [ ] T047 [US1] Test full workflow: Create course → Generate stage 1 → Generate stage 2 → Generate stage 3 → Export Markdown
- [ ] T048 [US1] Verify exported Markdown matches template structure in docs/UBD教案模板.md
- [ ] T049 [US1] Run semantic similarity test against golden standard V3 (≥80% threshold) using backend/app/tests/test_agents/test_golden_standard_v3.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 理解UbD理论并应用于教学设计 (Priority: P2)

**Goal**: 教师在使用系统过程中,通过UI中的引导式说明和AI生成内容的示范,逐步理解UbD逆向设计的三阶段思想,知道"为什么"这样设计课程

**Independent Test**: 用户访谈和问卷调查:在使用系统前后,教师对UbD核心概念的理解程度是否提升。观察用户是否能独立修改AI生成的内容且保持UbD逻辑一致性。

### UX Enhancements for Theory Learning

- [ ] T050 [P] [US2] Add inline UbD explanations above each input section in frontend-x/src/components/ChatPanel.tsx (using UbdTooltip)
- [ ] T051 [P] [US2] Create HelpDialog component with detailed UbD theory examples in frontend-x/src/components/HelpDialog.tsx
- [ ] T052 [P] [US2] Implement first-time user onboarding overlay in frontend-x/src/components/OnboardingOverlay.tsx (introduces G/U/Q/K/S concepts)
- [ ] T053 [US2] Add WHERETO principle labels to learning activities in MarkdownPreview component in frontend-x/src/components/MarkdownPreview.tsx
- [ ] T054 [US2] Highlight UbD element types in Markdown preview (U in blue, K in green, S in orange) in frontend-x/src/components/MarkdownPreview.tsx

### AI-Generated Content Quality Indicators

- [ ] T055 [P] [US2] Display validation_score for each U in ContentPanel in frontend-x/src/components/ContentPanel.tsx
- [ ] T056 [P] [US2] Show warnings for low-quality U (score < 0.7) with improvement suggestions in frontend-x/src/components/ContentPanel.tsx
- [ ] T057 [US2] Add "Why this is a good U?" explanation tooltip next to high-scoring U examples in frontend-x/src/components/UbdTooltip.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - 编辑和优化AI生成的课程内容 (Priority: P2)

**Goal**: 教师对AI生成的内容不完全满意时,可以直接在系统中编辑修改,并要求AI基于修改后的内容重新生成下游内容,确保整体课程方案的一致性

**Independent Test**: 修改模块1的某个U,然后观察模块2的表现性任务和模块3的学习蓝图是否能联动更新

### Editing Features

- [ ] T058 [P] [US3] Implement inline edit mode in MarkdownEditor with auto-save in frontend-x/src/components/MarkdownEditor.tsx
- [ ] T059 [P] [US3] Add edit confirmation and undo functionality in frontend-x/src/components/ContentPanel.tsx
- [ ] T060 [US3] Implement conversational modification (user sends "修改第一个U为..." in chat, AI updates content) in frontend-x/src/hooks/useChatConversation.ts

### Change Detection & Cascade Regeneration

- [ ] T061 [US3] Implement change detection API call when entering new step in frontend-x/src/hooks/useStepWorkflow.ts
- [ ] T062 [US3] Create ChangeDetectionDialog component to prompt regeneration in frontend-x/src/components/ChangeDetectionDialog.tsx
- [ ] T063 [US3] Add regeneration option for affected stages in frontend-x/src/services/workflowService.ts (POST /api/v1/workflow/stream with regenerate_stages param)
- [ ] T064 [US3] Update stage_versions timestamps on user edits in backend/app/api/v1/course.py (PUT /api/v1/courses/{id}/stage-{one|two|three})

### Conversation History Persistence

- [ ] T065 [P] [US3] Save user modification messages to conversation_history in backend/app/api/v1/course.py
- [ ] T066 [P] [US3] Save AI responses to conversation_history in backend/app/services/workflow_service.py
- [ ] T067 [US3] Load conversation history when re-entering a step in frontend-x/src/hooks/useChatConversation.ts

**Checkpoint**: All three main user stories should now be independently functional

---

## Phase 6: User Story 4 - 保存和管理多个课程项目 (Priority: P3)

**Goal**: 教师可以保存进行中的课程设计项目,在不同时间继续编辑,并管理多个课程项目

**Independent Test**: 创建多个课程项目,退出系统后重新登录,验证所有项目和进度都被正确保存和恢复

### Project Management UI

- [ ] T068 [P] [US4] Create ProjectListView component in frontend-x/src/components/ProjectListView.tsx (显示所有课程项目列表)
- [ ] T069 [P] [US4] Implement project search/filter functionality in frontend-x/src/components/ProjectListView.tsx
- [ ] T070 [P] [US4] Add project actions (delete, copy, archive) in frontend-x/src/components/ProjectListView.tsx

### Backend: Project CRUD

- [ ] T071 [P] [US4] Implement GET /api/v1/courses (list with pagination, search, filter) in backend/app/api/v1/course.py
- [ ] T072 [P] [US4] Implement DELETE /api/v1/courses/{id} in backend/app/api/v1/course.py
- [ ] T073 [P] [US4] Implement POST /api/v1/courses/{id}/copy (duplicate project) in backend/app/api/v1/course.py

### State Management

- [ ] T074 [US4] Add project list state to courseStore in frontend-x/src/stores/courseStore.ts
- [ ] T075 [US4] Implement navigation between ProjectListView and main App in frontend-x/src/App.tsx
- [ ] T076 [US4] Add "Save and Exit" button to return to project list in frontend-x/src/components/StepNavigator.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling

- [ ] T077 [P] Implement transparent error display for AI generation failures in frontend-x/src/components/ChatPanel.tsx (show specific error + retry option)
- [ ] T078 [P] Add timeout handling for SSE connections (120s timeout, heartbeat events) in backend/app/api/v1/generate.py
- [ ] T079 [P] Add error logging for all API endpoints in backend/app/core/logging.py

### Performance Optimization

- [ ] T080 [P] Implement lazy loading for step components (React.lazy + Suspense) in frontend-x/src/App.tsx
- [ ] T081 [P] Add debouncing to conversation message saving (500ms) in frontend-x/src/hooks/useChatConversation.ts
- [ ] T082 [P] Enable CodeMirror lazy loading (only load in edit mode) in frontend-x/src/components/MarkdownEditor.tsx

### Testing

- [ ] T083 [P] Run backend pytest suite (backend/app/tests/) per quickstart.md checklist
- [ ] T084 [P] Run frontend Vitest suite (frontend-x/src/) per quickstart.md checklist
- [ ] T085 [P] Run integration tests (full workflow, change detection, export) per quickstart.md checklist
- [ ] T086 Run golden standard V3 semantic similarity test (verify ≥80% for all stages)

### Documentation

- [ ] T087 [P] Update docs/UBD教案模板.md with V3 enhancements
- [ ] T088 [P] Create user guide with screenshots in docs/user-guide-v3.md
- [ ] T089 Run quickstart.md validation (verify all setup steps work)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 UI but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Requires US1 workflow but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- PHR v2 files before Agent class upgrades
- Models before services
- Services before API endpoints
- Backend APIs before frontend service calls
- Frontend components before integration
- Core implementation before integration tests

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story:
  - PHR v2 files can be written in parallel (T014-T016)
  - Models can be created in parallel (T020-T024)
  - Frontend components can be created in parallel (T030-T035)
  - Hooks can be created in parallel (T036-T038)
  - Services can be created in parallel (T039-T041)
  - Types can be defined in parallel (T042-T043)

---

## Parallel Example: User Story 1

```bash
# PHR v2 files (parallel):
Task T014: "Create project_foundation_v2.md in backend/app/prompts/phr/"
Task T015: "Create assessment_framework_v2.md in backend/app/prompts/phr/"
Task T016: "Create learning_blueprint_v2.md in backend/app/prompts/phr/"

# Models (parallel):
Task T020: "Update StageOneData model in backend/app/models/stage_data.py"
Task T021: "Update StageTwoData model in backend/app/models/stage_data.py"
Task T022: "Create PerformanceTask model in backend/app/models/performance_task.py"
Task T023: "Create Rubric model in backend/app/models/rubric.py"
Task T024: "Update StageThreeData model in backend/app/models/stage_data.py"

# Frontend Components (parallel):
Task T030: "Create ChatPanel component in frontend-x/src/components/ChatPanel.tsx"
Task T031: "Create ContentPanel component in frontend-x/src/components/ContentPanel.tsx"
Task T032: "Create MarkdownPreview component in frontend-x/src/components/MarkdownPreview.tsx"
Task T033: "Create MarkdownEditor component in frontend-x/src/components/MarkdownEditor.tsx"
Task T034: "Create UbdTooltip component in frontend-x/src/components/UbdTooltip.tsx"
Task T035: "Create DownloadButton component in frontend-x/src/components/DownloadButton.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013) - CRITICAL
3. Complete Phase 3: User Story 1 (T014-T049)
4. **STOP and VALIDATE**: Test User Story 1 independently against golden standard V3
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T013)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (T014-T049)
3. Add User Story 2 → Test independently → Deploy/Demo (T050-T057)
4. Add User Story 3 → Test independently → Deploy/Demo (T058-T067)
5. Add User Story 4 (optional) → Test independently → Deploy/Demo (T068-T076)
6. Polish Phase → Final production release (T077-T089)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - Developer A: User Story 1 Backend (T014-T029)
   - Developer B: User Story 1 Frontend (T030-T046)
   - Developer C: Can start on User Story 2 setup in parallel
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Frontend-x is a complete rewrite (ChatGPT-style UI), no code reuse from frontend-v2
- PHR v2 files MUST include change log documenting v1→v2 differences
- Conversation history persisted to database per research.md #8 decision
- SSE streaming chosen over parallel agent execution per research.md #6 decision
- Golden Standard V3 must be created based on docs/ubd教案案例一.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
