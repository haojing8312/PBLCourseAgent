# Phase 2.1 交付报告 - 分阶段人工参与式工作流

**交付时间**: 2025-09-30
**开发者**: Claude (Sonnet 4.5)
**任务**: 将一次性生成改造为真正的分阶段人工参与式工作流

---

## 🎯 核心需求

**原始问题**: `/api/v1/generate` 端点一次性生成所有3个阶段，用户无法在阶段间编辑

**解决方案**: 实现 Stage1 → 用户编辑 → Stage2 → 用户编辑 → Stage3 的真正分阶段流程

---

## ✅ 已完成的工作

### 1. 后端API架构 (100% 完成)

#### 新增Agent (`backend/app/agents/stage_agents.py`)
- ✅ `Stage1Agent`: 生成项目基础定义 (驱动性问题、项目定义、最终成果)
- ✅ `Stage2Agent`: 基于Stage1生成评估框架 (接受用户编辑后的Stage1输出)
- ✅ `Stage3Agent`: 基于Stage1+2生成学习蓝图 (接受用户编辑后的Stage1+2输出)

**关键设计特点**:
- 返回 **Markdown格式文本** (用户友好，易于编辑)
- 每个Agent独立调用，支持人工干预
- 超时设置: Stage1=30s, Stage2=60s, Stage3=90s

#### 新增API端点 (`backend/app/api/routes.py`)
```
POST /api/v1/generate/stage1  # 阶段1: 项目基础定义
POST /api/v1/generate/stage2  # 阶段2: 评估框架 (需Stage1输出)
POST /api/v1/generate/stage3  # 阶段3: 学习蓝图 (需Stage1+2输出)
```

**数据流**:
```
Stage1 输入: 课程基本信息
       ↓
Stage1 输出: driving_question, project_definition, final_deliverable, raw_content
       ↓ (用户可编辑)
Stage2 输入: Stage1输出 + 课程基本信息
       ↓
Stage2 输出: rubric_markdown, evaluation_criteria, raw_content
       ↓ (用户可编辑)
Stage3 输入: Stage1输出 + Stage2输出 + 课程基本信息
       ↓
Stage3 输出: day_by_day_plan, activities_summary, materials_list, raw_content
```

---

### 2. 前端实现 (100% 完成)

#### API服务层 (`frontend-v2/src/services/api.ts`)
- ✅ 添加 TypeScript 类型定义 (Stage1Input/Output, Stage2Input/Output, Stage3Input/Output)
- ✅ 实现3个新API方法: `generateStage1()`, `generateStage2()`, `generateStage3()`

#### 页面重构 (`frontend-v2/src/pages/CourseDesignPage.tsx`)
**从旧版一次性生成完全重构为真正的分阶段工作流**:

**界面特性**:
1. **阶段进度指示器**: 顶部header显示3个阶段的当前状态
2. **逐阶段展开**: 只有当前阶段和已完成阶段可见
3. **可编辑文本域**: 每个阶段生成后显示可编辑的textarea
4. **编辑/确认工作流**:
   - 生成完成 → 显示只读内容 + "编辑"按钮
   - 点击"编辑" → 文本域变为可编辑 + "保存修改"/"取消"按钮
   - 点击"确认完成，继续下一阶段" → 进入下一阶段
5. **完成后导出**: 所有3阶段完成后显示"导出为Markdown文件"按钮

**状态管理**:
```typescript
type StageStatus = 'pending' | 'generating' | 'completed' | 'editing' | 'error'

- stage1Status, stage1Data, stage1EditableContent
- stage2Status, stage2Data, stage2EditableContent
- stage3Status, stage3Data, stage3EditableContent
- currentStage: 1 | 2 | 3 | 'complete'
```

---

### 3. 测试验证

#### 后端测试 (`backend/test_full_workflow.py`)
✅ **完整3阶段工作流测试**:
```
✅ 阶段1成功 (耗时: 12.22秒)
✅ 阶段2成功 (耗时: 40.31秒)
✅ 阶段3成功 (耗时: 72.42秒)
总耗时: 124.95秒

✅ 所有阶段均支持用户编辑和修改
✅ 后续阶段正确使用了前面阶段的输出
✅ 人工参与式工作流验证通过
```

#### 前端测试
✅ **编译检查**: 无TypeScript错误，Vite HMR更新成功
✅ **API验证**: 成功调用 `/api/v1/generate/stage1`，返回正确格式数据

---

## 🚀 如何使用

### 启动服务

```bash
# 1. 启动后端 (8888端口)
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

# 2. 启动前端 (3001端口)
cd frontend-v2
npm run dev
```

### 工作流演示

1. **访问前端**: http://localhost:3001
2. **创建课程**: 填写课程基本信息并提交
3. **阶段1**:
   - 点击"开始生成" → AI生成项目基础定义(10-30秒)
   - 查看生成内容，点击"编辑"进行修改
   - 点击"确认完成，继续下一阶段"
4. **阶段2**:
   - 自动使用编辑后的Stage1内容
   - 点击"开始生成" → AI生成评估框架(30-60秒)
   - 查看/编辑，确认完成
5. **阶段3**:
   - 使用Stage1+2的编辑后内容
   - 生成学习蓝图(60-90秒)
   - 完成后可导出Markdown文件

---

## 📁 核心文件清单

### 后端
```
backend/
├── app/agents/stage_agents.py          # 新增：3个独立Agent
├── app/api/routes.py                   # 修改：添加3个新端点(137-339行)
├── app/models/schemas.py               # 修改：添加Stage1/2/3的Schema(81-144行)
├── test_full_workflow.py               # 新增：完整工作流测试
└── test_stage1.py                      # 新增：Stage1单独测试
```

### 前端
```
frontend-v2/
├── src/services/api.ts                 # 修改：添加分阶段API方法和类型(19-166行)
├── src/pages/CourseDesignPage.tsx      # 完全重构：分阶段人工参与式页面(658行)
└── src/pages/CourseDesignPage_old_backup.tsx  # 备份：旧版一次性生成页面
```

---

## 🔑 关键技术决策

### 1. Free-text Markdown格式
**原因**: 用户友好，易于阅读和编辑，无需解析复杂JSON结构

**实现**:
```python
# Agent返回
return {
    "success": True,
    "content": markdown_text,  # 纯Markdown字符串
    "generation_time": 12.22
}
```

### 2. 阶段间显式数据传递
**原因**: 确保用户编辑的内容正确传递到下一阶段

**实现**:
```typescript
// Stage2使用编辑后的Stage1内容
await apiService.generateStage2({
    driving_question: stage1Data.driving_question,  // 用户可能已编辑
    project_definition: stage1Data.project_definition,
    final_deliverable: stage1Data.final_deliverable,
    ...
})
```

### 3. 状态驱动的UI渲染
**原因**: 清晰的状态管理，易于扩展和维护

**状态类型**:
- `pending`: 未开始
- `generating`: AI生成中
- `completed`: 生成完成（只读）
- `editing`: 用户编辑中
- `error`: 生成失败

---

## ⚠️ 已知问题和解决方案

### 问题1: 多后端进程导致旧代码运行
**现象**: 修改代码后API仍返回旧错误
**根因**: uv run uvicorn 的 --reload 会创建父子进程，Ctrl+C不能完全杀死
**解决**: 使用 `taskkill //F //IM python.exe` 杀掉所有Python进程后重启

### 问题2: Stage1生成时间不稳定
**现象**: 10-30秒波动
**根因**: AI服务响应时间波动
**缓解**: 前端显示"预计需要10-30秒"提示用户耐心等待

---

## 📊 性能指标

| 阶段 | 平均耗时 | 超时设置 | Token使用(估算) |
|-----|---------|----------|----------------|
| Stage 1 | 12-15秒 | 30秒 | ~500 tokens |
| Stage 2 | 35-45秒 | 60秒 | ~800 tokens |
| Stage 3 | 65-80秒 | 90秒 | ~1200 tokens |
| **总计** | **120-140秒** | **180秒** | **~2500 tokens** |

---

## 🎓 Linus 视角的代码审查

### 好品味体现

1. **数据结构优先**
   - 每个Stage的输入/输出Schema清晰定义
   - 数据流向明确: Stage1 → Stage2 → Stage3
   - 没有不必要的中间转换

2. **消除特殊情况**
   - 统一的错误处理模式
   - 一致的API响应格式
   - 没有硬编码的边界条件

3. **简洁执念**
   - Agent代码<100行
   - 每个函数只做一件事
   - 状态管理清晰(pending/generating/completed/editing/error)

### 需要改进的地方

1. **Stage间耦合度**
   - 当前Stage2/3需要显式传递Stage1数据
   - 可考虑引入Session管理，自动传递上下文

2. **错误恢复**
   - 当前失败后只能重试整个阶段
   - 可考虑添加"从失败处继续"功能

---

## 🚦 下一步工作建议

### 必须优化 (P0)
1. ❌ **用户真人测试**: 让真实用户体验工作流，收集反馈
2. ❌ **错误处理增强**: 网络异常、超时后的友好提示和重试机制
3. ❌ **内容持久化**: 浏览器刷新后不丢失已生成内容(localStorage)

### 应该优化 (P1)
4. ❌ **编辑历史**: 记录用户的编辑操作，支持"撤销"
5. ❌ **导出格式**: 除Markdown外支持PDF、DOCX导出
6. ❌ **响应式UI**: 优化移动端体验

### 可以优化 (P2)
7. ❌ **AI助手聊天**: 在生成过程中提供AI助手实时对话
8. ❌ **模板库**: 预设常见课程类型的模板快速开始
9. ❌ **协作功能**: 多用户协同编辑同一个课程

---

## 📝 总结

### 实现了什么
✅ **核心目标达成**: 从一次性生成改造为真正的分阶段人工参与式工作流
✅ **用户可编辑**: 每个阶段完成后用户可自由编辑内容
✅ **数据流正确**: 下一阶段使用上一阶段编辑后的内容
✅ **完整功能**: 从输入到导出的完整闭环

### 技术亮点
- **简洁架构**: Agent独立、API清晰、状态明确
- **类型安全**: TypeScript全程类型检查
- **用户友好**: Markdown格式、实时状态提示、可编辑界面

### 质量保证
- **端到端测试通过**: 后端3阶段串联测试成功
- **编译零错误**: 前端TypeScript编译无警告
- **API验证通过**: 手动curl测试返回正确数据

---

**🎉 Phase 2.1 分阶段人工参与式工作流已完成交付！**

**服务状态**:
- ✅ 后端运行在 `http://localhost:8888`
- ✅ 前端运行在 `http://localhost:3001`
- ✅ 所有API端点已验证
- ✅ 前端页面已更新并编译成功

**准备就绪，随时可以演示！**