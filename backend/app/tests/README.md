# 测试文件说明

## 测试结构概览

本项目的测试套件分为三个层次：

### 1. 核心业务流程测试（最重要）⭐

**文件**: `test_core_workflow.py`

**作用**: 覆盖完整的用户业务流程，是最重要的测试文件。

**测试内容**:
- 创建课程（使用最新数据结构）
- 生成Stage 1（项目基础）
- 生成Stage 2（评估框架）
- 生成Stage 3（学习蓝图）
- 导出课程文档
- API契约验证

**何时必须运行**:
- ✅ 数据结构修改后
- ✅ 新API端点添加后
- ✅ Prompt重大修改后
- ✅ 提交PR前
- ✅ 每日开发结束前（如有重大修改）

**运行方式**:
```bash
cd backend

# 运行完整核心流程测试
uv run pytest app/tests/test_core_workflow.py -v

# 快速冒烟测试
uv run pytest app/tests/test_core_workflow.py::test_smoke_create_and_workflow -v

# 查看详细错误信息
uv run pytest app/tests/test_core_workflow.py -v --tb=short
```

### 2. 单元测试

针对各个Agent和Service的独立功能测试。

#### Agent测试

**`test_project_foundation_agent.py`**
- Agent 1（项目基础定义）的单元测试
- 测试G/U/Q/K/S框架生成
- 验证Markdown格式输出

**`test_assessment_framework_agent.py`**
- Agent 2（评估框架设计）的单元测试
- 测试驱动性问题和表现性任务生成
- 验证评估量规

**`test_learning_blueprint_agent.py`**
- Agent 3（学习蓝图生成）的单元测试
- 测试PBL四阶段学习计划
- 验证WHERETO原则应用

**`test_chat_agent.py`**
- Chat Agent的单元测试
- 测试对话驱动的课程方案修改
- 验证Markdown修改功能

#### Service测试

**`test_workflow_service.py`** ⚠️ **已过时**
- 测试旧版WorkflowService（非V3）
- 建议：在新开发中使用`test_core_workflow.py`代替

**`test_export_service.py`**
- 导出服务的单元测试
- 测试Markdown和JSON导出功能
- 验证导出格式正确性

#### 集成测试

**`test_export_integration.py`**
- 导出功能的集成测试
- 测试完整的导出流程

**`test_chat_integration.py`**
- Chat功能的集成测试
- 测试对话流程和Artifact生成

**`test_chat_artifact.py`**
- Chat Artifact的专项测试
- 验证Artifact生成和修改逻辑

### 3. 质量验证测试

**`test_golden_standard.py`**
- 使用黄金标准案例验证AI生成质量
- 测试生成内容是否符合预期标准
- 质量基准测试

**`test_main.py`**
- 基础API健康检查
- 验证应用启动和基本路由

## 快速开始

### 运行所有测试

```bash
cd backend

# 运行所有测试（包括可能较慢的AI生成测试）
uv run pytest app/tests/ -v

# 只运行快速测试（排除需要AI API的测试）
uv run pytest app/tests/ -v -m "not slow"
```

### 运行特定类型的测试

```bash
# 只运行核心业务流程测试
uv run pytest app/tests/test_core_workflow.py -v

# 只运行Agent单元测试
uv run pytest app/tests/test_*_agent.py -v

# 只运行冒烟测试
uv run pytest app/tests/ -v -m smoke
```

### 测试输出控制

```bash
# 显示详细输出
uv run pytest app/tests/test_core_workflow.py -v

# 显示print输出
uv run pytest app/tests/test_core_workflow.py -v -s

# 简短的traceback
uv run pytest app/tests/test_core_workflow.py -v --tb=short

# 只显示失败的测试
uv run pytest app/tests/test_core_workflow.py -v --tb=short -x
```

## 测试文件状态

| 文件名 | 状态 | 优先级 | 说明 |
|--------|------|--------|------|
| `test_core_workflow.py` | ✅ 活跃 | ⭐⭐⭐ 最高 | 核心业务流程测试，重大修改必须通过 |
| `test_project_foundation_agent.py` | ✅ 活跃 | ⭐⭐ 高 | Agent 1单元测试 |
| `test_assessment_framework_agent.py` | ✅ 活跃 | ⭐⭐ 高 | Agent 2单元测试 |
| `test_learning_blueprint_agent.py` | ✅ 活跃 | ⭐⭐ 高 | Agent 3单元测试 |
| `test_chat_agent.py` | ✅ 活跃 | ⭐⭐ 高 | Chat Agent单元测试 |
| `test_export_service.py` | ✅ 活跃 | ⭐ 中 | 导出服务单元测试 |
| `test_export_integration.py` | ✅ 活跃 | ⭐ 中 | 导出功能集成测试 |
| `test_chat_integration.py` | ✅ 活跃 | ⭐ 中 | Chat功能集成测试 |
| `test_chat_artifact.py` | ✅ 活跃 | ⭐ 中 | Chat Artifact测试 |
| `test_golden_standard.py` | ✅ 活跃 | ⭐ 中 | 质量基准测试 |
| `test_main.py` | ✅ 活跃 | ⭐ 中 | 基础健康检查 |
| `test_workflow_service.py` | ⚠️ 过时 | 低 | 测试旧版WorkflowService，建议归档 |

## 测试最佳实践

### 1. 重大修改时的测试流程

```bash
# 步骤1: 修改代码前，先了解当前测试
uv run pytest app/tests/test_core_workflow.py -v

# 步骤2: 修改代码...

# 步骤3: 立即运行核心测试
uv run pytest app/tests/test_core_workflow.py -v

# 步骤4: 如果测试失败，查看详细错误
uv run pytest app/tests/test_core_workflow.py -v --tb=short

# 步骤5: 修复并重新测试，直到全部通过
```

### 2. 数据结构修改检查清单

修改数据结构时，请参考CLAUDE.md中的详细检查清单，确保：

**后端**:
- [ ] `app/models/course_project.py` - 数据库模型
- [ ] `app/api/v1/course.py` - CRUD API
- [ ] `app/api/v1/generate.py` - Workflow API ⚠️ 容易遗漏
- [ ] `app/services/workflow_service_v3.py` - Service层
- [ ] 所有相关Agent的方法签名

**前端**:
- [ ] `src/types/course.ts` - TypeScript接口
- [ ] `src/stores/courseStore.ts` - 状态管理
- [ ] 所有使用该数据的组件

**测试**:
- [ ] `app/tests/test_core_workflow.py` - 核心流程测试

### 3. 测试驱动开发（TDD）建议

对于新功能开发：

```bash
# 1. 先写测试（描述期望行为）
# 编辑 test_core_workflow.py，添加新测试

# 2. 运行测试（应该失败）
uv run pytest app/tests/test_core_workflow.py::test_new_feature -v

# 3. 实现功能

# 4. 运行测试（应该通过）
uv run pytest app/tests/test_core_workflow.py::test_new_feature -v

# 5. 运行所有核心测试（确保没有破坏现有功能）
uv run pytest app/tests/test_core_workflow.py -v
```

## 常见问题

### Q: 测试失败，提示"Field required: duration_weeks"

**A**: 这是典型的API契约不一致问题。检查：
1. 是否所有API端点都已更新？（特别是`generate.py`）
2. 前后端字段名称是否完全一致？
3. 运行核心测试验证：`uv run pytest app/tests/test_core_workflow.py::test_02_workflow_api_accepts_new_fields -v`

### Q: 测试需要很长时间运行

**A**:
- 如果是AI生成测试，确认AI API可用且网络正常
- 可以先运行快速冒烟测试：`uv run pytest app/tests/test_core_workflow.py::test_smoke_create_and_workflow -v`
- 检查是否有超时设置

### Q: 某个Agent测试失败但核心流程测试通过

**A**:
- 核心流程测试优先级更高，如果通过说明核心功能正常
- Agent单元测试失败可能是测试本身需要更新
- 建议先修复核心流程测试，再处理单元测试

### Q: 如何添加新的测试？

**A**:
1. 对于新功能，首先在`test_core_workflow.py`中添加端到端测试
2. 如果需要详细的单元测试，创建新的test文件或添加到现有Agent测试中
3. 确保新测试遵循现有命名规范（`test_xxx`）

## 持续改进

如果发现：
- 某个测试文件已过时或不再使用
- 需要新的测试类型
- 测试流程可以优化

请更新此README.md并提PR说明原因。

## 参考资料

- 详细的测试规范：查看项目根目录的`CLAUDE.md`文件中的"核心业务流程测试规范"章节
- Pytest文档：https://docs.pytest.org/
- FastAPI测试文档：https://fastapi.tiangolo.com/tutorial/testing/
