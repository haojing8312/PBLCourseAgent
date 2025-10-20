# Data Model: UbD-PBL 课程架构师 V3

**Feature**: UbD-PBL 课程架构师 V3
**Date**: 2025-10-20
**Status**: Design Complete

## Purpose

定义UbD-PBL课程架构师V3所需的数据实体、字段、关系和验证规则。基于spec.md的Key Entities和research.md的设计决策。

## Entity Definitions

### 1. CourseProject (课程项目)

**Purpose**: 代表一个完整的UbD-PBL课程设计项目

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | PRIMARY KEY, NOT NULL | 项目唯一标识 |
| `title` | String(200) | NOT NULL | 课程名称 (如"0基础AI编程课程") |
| `subject` | String(100) | NULLABLE | 学科领域 (如"计算机科学", "数学") |
| `grade_level` | String(50) | NULLABLE | 年级水平 (如"高中", "大学一年级") |
| `duration_weeks` | Integer | DEFAULT 12, CHECK > 0 | 课程总时长(周数) |
| `current_stage` | Enum | NOT NULL, DEFAULT 'stage_one' | 当前所在阶段 ['stage_one', 'stage_two', 'stage_three', 'completed'] |
| `status` | Enum | NOT NULL, DEFAULT 'draft' | 项目状态 ['draft', 'in_progress', 'completed', 'archived'] |
| `created_at` | DateTime | NOT NULL, AUTO | 创建时间 |
| `updated_at` | DateTime | NOT NULL, AUTO_UPDATE | 最后更新时间 |
| `stage_versions` | JSON | NOT NULL, DEFAULT {} | 各阶段修改时间戳 {stage1_modified: ISO8601, stage2_modified: ISO8601, stage3_modified: ISO8601} |
| `conversation_history` | JSON | NOT NULL, DEFAULT {} | 每个步骤的对话历史 {1: Message[], 2: Message[], 3: Message[], 4: Message[]} |
| `user_id` | String(UUID) | FOREIGN KEY users.id, NULLABLE | 所属用户(MVP可暂时为NULL,单用户模式) |

**Relationships**:
- HAS ONE `StageOneData` (CASCADE DELETE)
- HAS ONE `StageTwoData` (CASCADE DELETE)
- HAS ONE `StageThreeData` (CASCADE DELETE)

**Indexes**:
- `idx_course_user_id` on `user_id`
- `idx_course_status` on `status`
- `idx_course_updated_at` on `updated_at` (for sorting project list)

**Validation Rules** (business logic):
- `title` must be 3-200 characters
- `duration_weeks` must be 1-52
- `current_stage` can only progress forward (stage_one→stage_two→stage_three→completed)
- `stage_versions` JSON must contain valid ISO8601 timestamps
- `conversation_history` JSON schema:
  ```typescript
  {
    [stepNumber: 1 | 2 | 3 | 4]: Array<{
      id: string;              // 消息唯一ID
      role: 'user' | 'assistant'; // 消息角色
      content: string;         // 消息内容
      timestamp: string;       // ISO8601时间戳
      metadata?: {             // 可选元数据
        action?: 'generate' | 'modify' | 'edit'; // 操作类型
        affectedFields?: string[]; // 影响的字段
      };
    }>
  }
  ```
  - 每个步骤的对话历史独立存储
  - `role='assistant'`的消息包含AI生成的完整回复
  - `role='user'`的消息包含用户的修改指令
  - 步骤完成后对话历史保留,用于用户回顾和调试

---

### 2. StageOneData (阶段一数据: 锚定深刻理解)

**Purpose**: 存储UbD阶段一的G/U/Q/K/S数据

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | PRIMARY KEY, NOT NULL | 数据唯一标识 |
| `course_project_id` | String(UUID) | FOREIGN KEY courses.id, UNIQUE, NOT NULL | 所属课程项目 |
| `goals` | JSON Array | NOT NULL, DEFAULT [] | 迁移目标(G) [{text: string, order: int}] |
| `understandings` | JSON Array | NOT NULL, DEFAULT [] | 持续理解(U) [{text: string, order: int, validation_score: float?}] |
| `questions` | JSON Array | NOT NULL, DEFAULT [] | 基本问题(Q) [{text: string, order: int}] |
| `knowledge` | JSON Array | NOT NULL, DEFAULT [] | 应掌握知识(K) [{text: string, order: int}] |
| `skills` | JSON Array | NOT NULL, DEFAULT [] | 应形成技能(S) [{text: string, order: int}] |
| `ai_generated_at` | DateTime | NULLABLE | AI生成时间(用于判断是否需要重新生成) |
| `user_modified_at` | DateTime | NULLABLE | 用户最后编辑时间 |

**Relationships**:
- BELONGS TO `CourseProject`

**Validation Rules**:
- 每个数组项的`text`字段不能为空字符串
- `order`字段必须>=0且唯一(同一数组内)
- `understandings.validation_score`范围0.0-1.0(可选,由validation_service生成)
- 建议数量: G(2-5), U(3-7), Q(2-4), K(<10), S(<10)

---

### 3. StageTwoData (阶段二数据: 设计评估证据)

**Purpose**: 存储UbD阶段二的驱动性问题、表现性任务和评估证据

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | PRIMARY KEY, NOT NULL | 数据唯一标识 |
| `course_project_id` | String(UUID) | FOREIGN KEY courses.id, UNIQUE, NOT NULL | 所属课程项目 |
| `driving_question` | Text | NOT NULL | 核心驱动性问题(PBL) |
| `driving_question_context` | Text | NULLABLE | 驱动性问题的情境描述 |
| `other_evidence` | JSON Array | DEFAULT [] | 其他评估证据 [{type: string, description: string}] (如观察记录, 测验, 反思日志) |
| `ai_generated_at` | DateTime | NULLABLE | AI生成时间 |
| `user_modified_at` | DateTime | NULLABLE | 用户最后编辑时间 |

**Relationships**:
- BELONGS TO `CourseProject`
- HAS MANY `PerformanceTask` (CASCADE DELETE)

**Validation Rules**:
- `driving_question` must be 10-500 characters and end with '?' or '。'
- 必须至少有1个`PerformanceTask`

---

### 4. PerformanceTask (表现性任务)

**Purpose**: 代表一个PBL表现性任务,作为解决驱动性问题的里程碑

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | PRIMARY KEY, NOT NULL | 任务唯一标识 |
| `stage_two_id` | String(UUID) | FOREIGN KEY stage_two.id, NOT NULL | 所属阶段二数据 |
| `title` | String(200) | NOT NULL | 任务标题 (如"社区问题调研报告") |
| `description` | Text | NOT NULL | 任务详细描述 |
| `context` | Text | NULLABLE | 真实情境说明 |
| `student_role` | String(100) | NULLABLE | 学生角色 (如"社区研究员", "AI工程师") |
| `deliverable` | Text | NOT NULL | 最终产出物描述 (如"5页调研报告+3分钟汇报") |
| `milestone_week` | Integer | CHECK > 0 | 对应的里程碑周次 (用于与Stage3活动对齐) |
| `order` | Integer | NOT NULL, DEFAULT 0 | 任务顺序(第1个, 第2个...) |
| `linked_ubd_elements` | JSON | DEFAULT {} | 关联的UbD目标 {u: [1,2], s: [1], k: [3,4]} (数字对应order) |

**Relationships**:
- BELONGS TO `StageTwoData`
- HAS MANY `Rubric` (CASCADE DELETE)

**Indexes**:
- `idx_task_stage_two_order` on (`stage_two_id`, `order`)

**Validation Rules**:
- `title` must be 3-200 characters
- `deliverable` must be non-empty
- `milestone_week` must be <= CourseProject.duration_weeks
- `order` must be unique within same `stage_two_id`

---

### 5. Rubric (评估量规)

**Purpose**: 为表现性任务定义评估维度和等级标准

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | PRIMARY KEY, NOT NULL | 量规唯一标识 |
| `performance_task_id` | String(UUID) | FOREIGN KEY tasks.id, NOT NULL | 所属表现性任务 |
| `name` | String(100) | NOT NULL | 量规名称 (如"社区问题调研评估量规") |
| `dimensions` | JSON Array | NOT NULL | 评估维度 [{name: string, weight: float?, levels: [{level: int, label: string, description: string}]}] |

**Example JSON Structure for `dimensions`**:
```json
[
  {
    "name": "问题识别与分析",
    "weight": 0.3,
    "levels": [
      {"level": 1, "label": "初学", "description": "能识别1-2个表面问题..."},
      {"level": 2, "label": "发展中", "description": "能识别3-4个问题并尝试分类..."},
      {"level": 3, "label": "熟练", "description": "能识别5+问题,清晰分类并初步分析根因..."},
      {"level": 4, "label": "优秀", "description": "能系统识别问题,深度分析根因并提出见解..."}
    ]
  },
  {
    "name": "数据收集与验证",
    "weight": 0.3,
    "levels": [...]
  }
]
```

**Relationships**:
- BELONGS TO `PerformanceTask`

**Validation Rules**:
- `dimensions` must be non-empty array
- Each dimension must have 4-5 levels (对应Constitution VI要求的四级量规)
- Each level must have unique `level` number (1-5)
- Weights (if provided) must sum to 1.0

---

### 6. StageThreeData (阶段三数据: 规划PBL学习体验)

**Purpose**: 存储UbD阶段三的PBL学习蓝图

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | PRIMARY KEY, NOT NULL | 数据唯一标识 |
| `course_project_id` | String(UUID) | FOREIGN KEY courses.id, UNIQUE, NOT NULL | 所属课程项目 |
| `phases` | JSON Array | NOT NULL, DEFAULT [] | PBL阶段列表 (预设4阶段结构,见下方JSON schema) |
| `ai_generated_at` | DateTime | NULLABLE | AI生成时间 |
| `user_modified_at` | DateTime | NULLABLE | 用户最后编辑时间 |

**Example JSON Structure for `phases`**:
```json
[
  {
    "type": "launch",
    "name": "项目启动",
    "duration_weeks": 1,
    "description": "介绍项目背景,提出驱动性问题,激发学习动机",
    "activities": [
      {
        "id": "uuid",
        "title": "专家讲座: AI在社区中的应用",
        "description": "邀请企业AI工程师...",
        "duration_days": 1,
        "order": 0,
        "ubd_labels": ["U1", "Q1"],
        "whereto_labels": ["H-Hook"]
      }
    ]
  },
  {
    "type": "build",
    "name": "知识与技能构建",
    "duration_weeks": 4,
    "activities": [...]
  },
  {
    "type": "develop",
    "name": "开发与迭代",
    "duration_weeks": 5,
    "activities": [...]
  },
  {
    "type": "present",
    "name": "成果展示与反思",
    "duration_weeks": 2,
    "activities": [...]
  }
]
```

**Relationships**:
- BELONGS TO `CourseProject`
- Activities implicitly reference `LearningActivity` (embedded in JSON)

**Validation Rules**:
- `phases` must have exactly 4 elements with types ['launch', 'build', 'develop', 'present'] in order
- Sum of `phases[*].duration_weeks` should equal `CourseProject.duration_weeks` (允许±1周误差)
- Each activity must have unique `id` within the entire phases array
- `ubd_labels` format: ["U{order}", "S{order}", "K{order}", "Q{order}"]
- `whereto_labels` format: ["H-Hook", "E-Explore", "R-Rethink", ...] (7个WHERETO原则)

---

### 7. LearningActivity (学习活动 - 已嵌入StageThreeData.phases)

**Note**: 为简化MVP实现,LearningActivity不作为独立表,而是嵌入在`StageThreeData.phases[*].activities`的JSON数组中。未来如需高级查询(如按UbD目标过滤活动),可重构为独立表。

**Embedded Schema** (within JSON):

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | String(UUID) | UNIQUE | 活动唯一标识(用于前端编辑操作) |
| `title` | String(200) | NOT NULL | 活动标题 |
| `description` | Text | NOT NULL | 活动详细描述 |
| `duration_days` | Integer | CHECK > 0 | 活动时长(天数) |
| `order` | Integer | NOT NULL | 活动在本阶段内的顺序 |
| `ubd_labels` | Array of String | DEFAULT [] | 关联的UbD目标标签 (如["U1", "S2", "K3"]) |
| `whereto_labels` | Array of String | DEFAULT [] | 对应的WHERETO原则标签 (如["H-Hook", "E-Explore"]) |

**Validation Rules**:
- `title` must be 3-200 characters
- `ubd_labels` elements must match pattern `[USQKG]\d+` (如U1, S10, Q2)
- `whereto_labels` must be from predefined set: ["W-Where", "H-Hook", "E-Explore", "R-Rethink", "E-Equip", "T-Tailor", "O-Organize"]

---

### 8. ExportTemplate (导出模板)

**Purpose**: 定义教案导出的格式模板(Markdown/PDF)

**Implementation Note**: MVP阶段使用硬编码的Jinja2模板文件(`docs/UBD教案模板.md`),不作为数据库表。未来支持用户自定义模板时再设计此表。

**Deferred to Post-MVP** - 不在V3范围内实现

---

## Data Model Diagram (Entity Relationship)

```
┌─────────────────┐
│  CourseProject  │
│  ─────────────  │
│  id             │
│  title          │
│  current_stage  │
│  stage_versions │
│  ...            │
└────────┬────────┘
         │ 1
         ├─────────────┐
         │ 1           │ 1
    ┌────▼────┐   ┌────▼────┐   ┌────────────┐ 1
    │ Stage   │   │ Stage   │   │ Stage      │
    │ One     │   │ Two     │   │ Three      │
    │ Data    │   │ Data    │   │ Data       │
    └─────────┘   └────┬────┘   └────────────┘
                       │ 1
                       │
                       │ *
              ┌────────▼──────────┐
              │ PerformanceTask   │
              │  ────────────────  │
              │  title             │
              │  milestone_week    │
              │  linked_ubd_elem   │
              └────────┬───────────┘
                       │ 1
                       │
                       │ *
                  ┌────▼──────┐
                  │  Rubric   │
                  │  ───────  │
                  │  name     │
                  │  dimensions│
                  └───────────┘
```

---

## Migration Strategy (向后兼容V2)

### Current V2 Schema (assumed structure)

```python
# V2可能的结构(需确认实际代码)
class CourseProjectV2:
    id, title, subject, grade_level, status, created_at, updated_at
    stage_one_json: JSON  # 可能是扁平JSON
    stage_two_json: JSON
    stage_three_json: JSON
```

### V3 Migration Plan

1. **Schema Evolution**:
   - 拆分V2的`stage_*_json`为独立表(StageOneData, StageTwoData, StageThreeData)
   - 添加`stage_versions`字段到CourseProject
   - 创建PerformanceTask和Rubric独立表

2. **Data Migration Script**:
   ```python
   # backend/app/migrations/v2_to_v3.py
   def migrate_course_project(v2_course):
       # 创建V3 CourseProject
       v3_course = CourseProject(
           id=v2_course.id,
           title=v2_course.title,
           # ... copy common fields
           stage_versions={
               'stage1_modified': v2_course.updated_at,
               'stage2_modified': v2_course.updated_at,
               'stage3_modified': v2_course.updated_at
           }
       )

       # 迁移Stage One
       stage_one_data = StageOneData(
           course_project_id=v3_course.id,
           goals=[{'text': g, 'order': i} for i, g in enumerate(v2_course.stage_one_json.get('G', []))],
           understandings=[{'text': u, 'order': i} for i, u in enumerate(v2_course.stage_one_json.get('U', []))],
           # ... similar for Q, K, S
       )

       # 迁移Stage Two (需解析原JSON结构)
       # 迁移Stage Three (需解析原JSON结构,转换为PBL 4阶段)

       return v3_course, stage_one_data, ...
   ```

3. **Rollback Plan**:
   - 保留V2表结构(重命名为`course_projects_v2_backup`)
   - 提供回滚脚本将V3数据重新序列化回V2格式

---

## Database Indexes and Performance

### Critical Indexes (必须创建)

```sql
-- CourseProject
CREATE INDEX idx_course_user_id ON course_projects(user_id);
CREATE INDEX idx_course_status ON course_projects(status);
CREATE INDEX idx_course_updated_at ON course_projects(updated_at DESC);

-- PerformanceTask
CREATE INDEX idx_task_stage_two_order ON performance_tasks(stage_two_id, "order");

-- Composite index for change detection
CREATE INDEX idx_course_stage_versions ON course_projects USING GIN(stage_versions);
```

### Query Performance Targets

- 课程列表加载(100项): <200ms
- 单个课程完整数据加载(含所有Stage): <300ms
- 变更检测查询: <50ms
- Rubric查询(for导出): <100ms

---

## Validation Rules Summary

### Stage One (StageOneData)
- ✅ G: 2-5项,每项10-200字符
- ✅ U: 3-7项,每项10-500字符,必须通过UbD验证(抽象观点)
- ✅ Q: 2-4项,每项必须以'?'或'?'结尾
- ✅ K: ≤10项,每项5-200字符
- ✅ S: ≤10项,每项5-200字符,必须包含动词

### Stage Two (StageTwoData + PerformanceTask + Rubric)
- ✅ 驱动性问题: 10-500字符,必须以'?'或'?'结尾
- ✅ 至少1个PerformanceTask
- ✅ 每个Task的milestone_week必须<=课程总周数
- ✅ Rubric维度: 2-6个维度,每个维度4-5个等级

### Stage Three (StageThreeData)
- ✅ 必须有4个阶段(launch, build, develop, present),按顺序
- ✅ 阶段总时长=课程总周数(±1周容差)
- ✅ 每个活动的ubd_labels必须引用Stage One中存在的元素
- ✅ whereto_labels必须来自预定义的7个标签

---

## Next Steps for Implementation

1. **ORM Models**: 在`backend/app/models/`中实现SQLAlchemy models
2. **Migration Scripts**: 使用Alembic创建数据库迁移
3. **Pydantic Schemas**: 在`backend/app/schemas/`中创建API请求/响应schema
4. **TypeScript Types**: 在`frontend-v2/src/types/course.ts`中生成对应的TS接口
5. **Validation Service**: 实现`backend/app/services/validation_service.py`中的验证逻辑
6. **Test Fixtures**: 创建测试用的golden standard数据符合新schema

数据模型设计完成,可进入API合约设计。
