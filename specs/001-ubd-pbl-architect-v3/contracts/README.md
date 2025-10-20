# API Contracts: UbD-PBL 课程架构师 V3

## Overview

This directory contains the API contract specifications for the UbD-PBL Course Architect V3.

## Files

- **`openapi.yaml`**: Complete OpenAPI 3.0 specification for all REST API endpoints
- **`README.md`**: This file - usage guide and examples

## Key Endpoints

### Core Workflow

```
POST   /api/v1/courses                        # Create new course project
POST   /api/v1/workflow/stream?courseId={id}  # Execute 3-stage AI workflow (SSE)
GET    /api/v1/courses/{id}                   # Get full course data
POST   /api/v1/courses/{id}/export            # Export to Markdown/PDF
```

### Stage Editing

```
GET    /api/v1/courses/{id}/stage-one         # Get G/U/Q/K/S
PUT    /api/v1/courses/{id}/stage-one         # Update G/U/Q/K/S (user edits)
GET    /api/v1/courses/{id}/stage-two         # Get driving question + tasks
PUT    /api/v1/courses/{id}/stage-two         # Update stage two data
GET    /api/v1/courses/{id}/stage-three       # Get PBL blueprint
PUT    /api/v1/courses/{id}/stage-three       # Update PBL blueprint
```

### Validation & Change Detection

```
POST   /api/v1/validate/ubd-element           # Validate U vs K, Q format, etc.
GET    /api/v1/courses/{id}/changes?target_stage=2  # Detect upstream changes
```

## Usage Examples

### 1. Create a New Course Project

**Request:**
```http
POST /api/v1/courses HTTP/1.1
Content-Type: application/json

{
  "title": "0基础AI编程课程",
  "subject": "计算机科学",
  "grade_level": "高中",
  "duration_weeks": 12
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-course-id",
    "title": "0基础AI编程课程",
    "subject": "计算机科学",
    "grade_level": "高中",
    "duration_weeks": 12,
    "current_stage": "stage_one",
    "status": "draft",
    "created_at": "2025-10-20T10:00:00Z",
    "updated_at": "2025-10-20T10:00:00Z",
    "stage_versions": {}
  }
}
```

---

### 2. Execute Full Workflow with SSE Progress

**Request:**
```http
POST /api/v1/workflow/stream?courseId=uuid-course-id HTTP/1.1
Content-Type: application/json
Accept: text/event-stream

{
  "regenerate_stages": [1, 2, 3]
}
```

**SSE Response Stream:**
```
data: {"type": "agent_start", "agent": "stage_one", "percent": 0}

data: {"type": "agent_progress", "agent": "stage_one", "percent": 50}

data: {"type": "agent_complete", "agent": "stage_one", "percent": 100, "result": {...stage_one_data}}

data: {"type": "agent_start", "agent": "stage_two", "percent": 0}

data: {"type": "agent_progress", "agent": "stage_two", "percent": 60}

data: {"type": "agent_complete", "agent": "stage_two", "percent": 100, "result": {...stage_two_data}}

data: {"type": "agent_start", "agent": "stage_three", "percent": 0}

data: {"type": "agent_complete", "agent": "stage_three", "percent": 100, "result": {...stage_three_data}}

data: {"type": "workflow_complete", "success": true}
```

**Frontend EventSource Code:**
```typescript
const eventSource = new EventSource(`/api/v1/workflow/stream?courseId=${courseId}`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case 'agent_start':
      console.log(`Starting ${data.agent}...`);
      break;
    case 'agent_progress':
      console.log(`${data.agent}: ${data.percent}%`);
      break;
    case 'agent_complete':
      console.log(`${data.agent} completed!`, data.result);
      break;
    case 'workflow_complete':
      eventSource.close();
      console.log('All done!');
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

---

### 3. Edit Stage One (User modifies U)

**Request:**
```http
PUT /api/v1/courses/uuid-course-id/stage-one HTTP/1.1
Content-Type: application/json

{
  "understandings": [
    {"text": "AI是一把双刃剑,既能带来便利也可能造成风险", "order": 0},
    {"text": "技术伦理需要在开发和应用的每个阶段考虑", "order": 1}
  ],
  "goals": [...],
  "questions": [...],
  "knowledge": [...],
  "skills": [...]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "stage-one-uuid",
    "course_project_id": "uuid-course-id",
    "understandings": [
      {
        "text": "AI是一把双刃剑,既能带来便利也可能造成风险",
        "order": 0,
        "validation_score": 0.92
      },
      {
        "text": "技术伦理需要在开发和应用的每个阶段考虑",
        "order": 1,
        "validation_score": 0.88
      }
    ],
    ...
    "user_modified_at": "2025-10-20T10:30:00Z"
  },
  "warnings": []
}
```

---

### 4. Detect Upstream Changes (for联动regeneration)

**Request:**
```http
GET /api/v1/courses/uuid-course-id/changes?target_stage=2 HTTP/1.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stage1_changed": true,
    "stage2_changed": false,
    "affected_stages": [2, 3],
    "last_modified_times": {
      "stage1": "2025-10-20T10:30:00Z",
      "stage2": "2025-10-20T10:00:00Z"
    }
  }
}
```

**Frontend Logic:**
```typescript
const checkChanges = async (courseId: string, targetStage: number) => {
  const response = await fetch(`/api/v1/courses/${courseId}/changes?target_stage=${targetStage}`);
  const result = await response.json();

  if (result.data.stage1_changed || result.data.stage2_changed) {
    const shouldRegenerate = confirm(
      `检测到阶段${result.data.stage1_changed ? '一' : '二'}的变更,是否重新生成评估设计?`
    );

    if (shouldRegenerate) {
      // Trigger workflow stream for affected stages
      const stream = new EventSource(`/api/v1/workflow/stream?courseId=${courseId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({regenerate_stages: result.data.affected_stages})
      });
      // Handle stream...
    }
  }
};
```

---

### 5. Validate UbD Element (U vs K check)

**Request:**
```http
POST /api/v1/validate/ubd-element HTTP/1.1
Content-Type: application/json

{
  "element_type": "U",
  "text": "学生将掌握Python编程语法"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_valid": false,
    "confidence": 0.35,
    "warnings": [
      {
        "field": "understandings",
        "message": "此陈述更像是一个技能(S)或知识点(K),而非抽象的持续理解(U)。建议修改为: '理解编程语言如何成为表达思想和解决问题的工具'",
        "severity": "warning"
      }
    ]
  }
}
```

---

### 6. Export Course Plan to Markdown

**Request:**
```http
POST /api/v1/courses/uuid-course-id/export HTTP/1.1
Content-Type: application/json

{
  "format": "markdown"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/markdown
Content-Disposition: attachment; filename="0基础AI编程课程_UbD-PBL教案.md"

# 课程名称: 0基础AI编程课程
**设计理念**: 本课程采用"为理解而设计"(UbD)作为核心设计框架,以"项目式学习"(PBL)作为主要的教学实施模式...

## 阶段一：确定预期学习结果
...
```

---

### 7. Save and Retrieve Conversation History

**Save a user message:**
```http
POST /api/v1/courses/uuid-course-id/conversation HTTP/1.1
Content-Type: application/json

{
  "step": 1,
  "message": {
    "role": "user",
    "content": "请将第一个U修改为更抽象的表述",
    "metadata": {
      "action": "modify",
      "affectedFields": ["understandings[0]"]
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "msg-uuid-123",
    "timestamp": "2025-10-20T11:00:00Z"
  }
}
```

**Save an AI response:**
```http
POST /api/v1/courses/uuid-course-id/conversation HTTP/1.1
Content-Type: application/json

{
  "step": 1,
  "message": {
    "role": "assistant",
    "content": "好的,我已经将第一个持续理解(U)修改为: \"AI技术是一把双刃剑,既能带来便利也可能造成风险\"。这个表述更加抽象,强调了对AI本质的理解,而非具体的技术知识点。",
    "metadata": {
      "action": "modify",
      "affectedFields": ["understandings[0]"]
    }
  }
}
```

**Get conversation history for a step:**
```http
GET /api/v1/courses/uuid-course-id/conversation?step=1 HTTP/1.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "step": 1,
    "messages": [
      {
        "id": "msg-uuid-001",
        "role": "assistant",
        "content": "我已经为您生成了阶段一的内容,包含3个持续理解(U)、2个迁移目标(G)...",
        "timestamp": "2025-10-20T10:00:00Z",
        "metadata": {"action": "generate"}
      },
      {
        "id": "msg-uuid-002",
        "role": "user",
        "content": "请将第一个U修改为更抽象的表述",
        "timestamp": "2025-10-20T11:00:00Z",
        "metadata": {"action": "modify", "affectedFields": ["understandings[0]"]}
      },
      {
        "id": "msg-uuid-003",
        "role": "assistant",
        "content": "好的,我已经将第一个持续理解(U)修改为...",
        "timestamp": "2025-10-20T11:00:05Z",
        "metadata": {"action": "modify", "affectedFields": ["understandings[0]"]}
      }
    ]
  }
}
```

**Frontend Integration Example:**
```typescript
// Save user message
const saveUserMessage = async (courseId: string, step: number, content: string) => {
  await fetch(`/api/v1/courses/${courseId}/conversation`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      step,
      message: {role: 'user', content}
    })
  });
};

// Load conversation history on step entry
const loadConversationHistory = async (courseId: string, step: number) => {
  const response = await fetch(`/api/v1/courses/${courseId}/conversation?step=${step}`);
  const result = await response.json();
  return result.data.messages;
};
```

---

## Error Handling

All endpoints follow the same error response structure:

```json
{
  "success": false,
  "message": "Human-readable error message",
  "error": "ERROR_CODE",
  "details": {
    "field": "specific_field_name",
    "reason": "validation_failed"
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR`: Request body validation failed
- `NOT_FOUND`: Resource not found
- `AI_SERVICE_UNAVAILABLE`: AI generation service is down
- `AI_GENERATION_FAILED`: AI returned empty or invalid content
- `STAGE_DEPENDENCY_ERROR`: Trying to access stage 2 before completing stage 1

**Example Error Response:**
```json
{
  "success": false,
  "message": "AI生成服务当前不可用,请稍后重试",
  "error": "AI_SERVICE_UNAVAILABLE",
  "details": {
    "retry_after_seconds": 60,
    "service_status": "timeout"
  }
}
```

---

## Rate Limiting

- **General APIs**: 100 requests/minute per user
- **AI Workflow (`/workflow/stream`)**: 5 requests/minute per user (to prevent abuse)
- **Export**: 10 requests/minute per user

Exceeding limits returns `429 Too Many Requests` with `Retry-After` header.

---

## Testing the API

### Using cURL

```bash
# Create course
curl -X POST http://localhost:8000/api/v1/courses \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Course", "duration_weeks": 8}'

# Get course
curl http://localhost:8000/api/v1/courses/{courseId}

# SSE stream (use --no-buffer for real-time output)
curl -N --no-buffer http://localhost:8000/api/v1/workflow/stream?courseId={courseId} \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"regenerate_stages": [1,2,3]}'
```

### Using OpenAPI Tools

Generate client SDK:
```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate TypeScript client
openapi-generator-cli generate \
  -i contracts/openapi.yaml \
  -g typescript-fetch \
  -o frontend-v2/src/api-client

# Generate Python client (for testing)
openapi-generator-cli generate \
  -i contracts/openapi.yaml \
  -g python \
  -o backend/tests/api-client
```

---

## Versioning

- **API Version**: v1 (stable)
- **Contract Version**: 3.0.0 (matches feature version)
- **Breaking changes**: Will be released as v2

---

## See Also

- [Data Model](../data-model.md) - Database schema and entity definitions
- [Research](../research.md) - Design decisions and alternatives considered
- [Specification](../spec.md) - Feature requirements and acceptance criteria

---

**Last Updated**: 2025-10-20
**Contact**: PBLCourseAgent Team
