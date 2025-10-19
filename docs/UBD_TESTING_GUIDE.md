# UBD 课程设计系统 - 测试指南

## 目录
1. [环境配置](#环境配置)
2. [启动服务](#启动服务)
3. [功能测试](#功能测试)
4. [验收标准](#验收标准)

---

## 环境配置

### 1. API Key 配置

在 `jaaz/server/.env` 文件中配置有效的 AI API密钥：

```bash
# 使用 DeepSeek API（推荐）
PBL_AI_API_KEY=your_deepseek_api_key_here
PBL_AI_MODEL=deepseek-chat
PBL_AI_BASE_URL=https://api.deepseek.com/v1

# 或使用 OpenAI API
# PBL_AI_API_KEY=your_openai_api_key_here
# PBL_AI_MODEL=gpt-4
# PBL_AI_BASE_URL=https://api.openai.com/v1

# 或使用其他兼容 OpenAI API 的服务
# PBL_AI_API_KEY=your_api_key_here
# PBL_AI_MODEL=your_model_name
# PBL_AI_BASE_URL=your_api_base_url
```

### 2. 安装依赖

```bash
# 后端依赖
cd jaaz/server
uv sync

# 前端依赖（如果需要）
cd jaaz/react
npm install
```

---

## 启动服务

### 方式一：自动启动（推荐）

使用以下命令同时启动前后端服务：

```bash
# 在 jaaz 目录下
cd jaaz/server
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

cd ../react
npm run dev &
```

### 方式二：分别启动

**后端服务：**
```bash
cd jaaz/server
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 `http://localhost:8000` 运行

**前端服务：**
```bash
cd jaaz/react
npm run dev
```

前端服务将在 `http://localhost:5174` 运行

---

## 功能测试

### 测试 1: 模式选择界面

1. 打开浏览器访问 `http://localhost:5174`
2. 点击 "New Canvas" 创建新画布
3. 应该看到模式选择对话框：
   - ✅ Design Mode（设计模式）- 用于图像/视频生成
   - ✅ Course Mode（课程模式）- 用于 UBD 课程设计

**验收标准：**
- [ ] 模式选择界面正常显示
- [ ] 两种模式都可以选择
- [ ] 选择后创建相应类型的画布

---

### 测试 2: UBD 课程设计工作流

1. 选择 **Course Mode** 创建画布
2. 在聊天界面输入以下测试消息：

```
设计一门关于"智能机器人编程"的初中科技课程，包含以下要求：

课程背景：
- 年级：初中7-8年级
- 学时：16课时（每课时45分钟）
- 学生基础：有基础的Scratch编程经验

核心目标：
- 让学生掌握基础的机器人编程技能
- 培养计算思维和问题解决能力
- 了解人工智能和传感器的基本原理
- 完成一个实际的机器人项目

项目要求：
- 使用Arduino或类似硬件平台
- 包含传感器应用（如超声波、红外、温度等）
- 完成一个解决实际问题的机器人项目（如避障小车、自动灌溉系统等）

请按照UBD框架设计完整的课程方案。
```

3. 观察系统执行流程

**预期行为：**
1. **Agent 执行顺序：**
   - `ubd_planner` - 分析需求并规划工作流
   - `project_foundation_agent` - 定义项目基础（Stage 1）
   - `assessment_designer` - 设计评估框架（Stage 2）
   - `blueprint_generator` - 生成学习蓝图（Stage 3）

2. **文档卡片生成：**
   - 在画布上应该出现 3 个文档卡片：
     - 📘 Stage 1: Project Foundation
     - 📗 Stage 2: Assessment Framework
     - 📙 Stage 3: Learning Blueprint

3. **文档卡片功能：**
   - [ ] 文档卡片可以拖动
   - [ ] 文档内容以 Markdown 格式显示
   - [ ] 可以复制文档内容
   - [ ] 可以下载单个文档
   - [ ] 可以删除文档卡片

**验收标准：**
- [ ] 4个 Agent 按顺序执行
- [ ] 生成了 3 个文档卡片
- [ ] 文档内容符合 UBD 框架要求
- [ ] 所有卡片功能正常工作

---

### 测试 3: 导出 Markdown 功能

1. 完成测试 2 后，点击画布右上角的 **"Export Course"** 按钮
2. 系统应该下载一个 Markdown 文件

**预期结果：**
- 文件名格式：`UBD_Course_Design_YYYY-MM-DD.md`
- 文件内容包含：
  - 课程标题和生成时间
  - Stage 1: Project Foundation 完整内容
  - Stage 2: Assessment Framework 完整内容
  - Stage 3: Learning Blueprint 完整内容
  - 各阶段之间有分隔线

**验收标准：**
- [ ] 成功下载 Markdown 文件
- [ ] 文件包含所有 3 个阶段的内容
- [ ] 内容格式正确，易于阅读
- [ ] 可以用任何 Markdown 编辑器打开

---

### 测试 4: 单元测试

运行后端单元测试：

```bash
cd jaaz/server
uv run pytest tests/test_ubd_integration.py -v
```

**预期结果：**
```
tests/test_ubd_integration.py::TestUBDIntegration::test_ubd_planner_config PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_project_foundation_config PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_assessment_designer_config PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_blueprint_generator_config PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_ubd_tools_registration PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_define_project_foundation_tool PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_design_assessment_framework_tool PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_generate_learning_blueprint_tool PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_workflow_configuration PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_agent_name_conventions PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_ubd_mode_detection PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_tool_integration PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_complete_workflow_structure PASSED
tests/test_ubd_integration.py::TestUBDIntegration::test_swarm_configuration PASSED

================================ 14 passed in X.XXs ================================
```

**验收标准：**
- [ ] 所有 14 个测试全部通过
- [ ] 无任何错误或警告

---

### 测试 5: 端到端测试（需要有效 API Key）

```bash
cd jaaz/server
uv run python test_ubd_e2e.py
```

**预期结果：**
```
================================================================================
UBD COURSE DESIGN - END-TO-END TEST
================================================================================
...
✅ Test Results:
   All agents called: True
   All documents generated: True
   Total messages: X
   Total documents: 3

🎉 SUCCESS: UBD workflow completed successfully!

================================================================================
✅ ALL TESTS PASSED
================================================================================
```

**验收标准：**
- [ ] 所有 4 个 Agent 被调用
- [ ] 生成了 3 个文档事件
- [ ] 测试结果显示成功

---

## 验收标准总结

### 核心功能（必须）
- ✅ **模式选择**：用户可以选择 Design 或 Course 模式
- ✅ **UBD 工作流**：4个 Agent 按正确顺序执行
- ✅ **文档生成**：生成 3 个符合 UBD 框架的文档卡片
- ✅ **文档展示**：文档卡片正确显示 Markdown 内容
- ✅ **导出功能**：可以导出完整的课程设计为 Markdown 文件

### 交互功能（必须）
- ✅ **拖动卡片**：文档卡片可以在画布上自由拖动
- ✅ **复制内容**：可以复制文档内容到剪贴板
- ✅ **下载文档**：可以下载单个文档
- ✅ **删除卡片**：可以删除不需要的文档卡片

### 质量标准（必须）
- ✅ **单元测试**：14/14 测试通过
- ✅ **代码质量**：无明显错误，符合最佳实践
- ✅ **用户体验**：流程清晰，操作直观
- ✅ **文档质量**：生成的内容符合教学设计标准

---

## 常见问题

### Q1: API Key 错误
**错误信息：** `Error code: 401 - account_deactivated`

**解决方案：**
1. 检查 `.env` 文件中的 `PBL_AI_API_KEY` 是否正确
2. 确认 API key 仍然有效
3. 尝试使用不同的 AI 服务提供商

### Q2: 文档卡片不显示
**可能原因：**
1. WebSocket 连接失败
2. 后端未正确发送文档事件

**解决方案：**
1. 检查浏览器控制台是否有 WebSocket 错误
2. 检查后端日志是否有 "📤 Sent document event" 消息
3. 刷新页面重试

### Q3: 导出功能不工作
**可能原因：**
1. 文档卡片数组为空
2. 浏览器阻止了文件下载

**解决方案：**
1. 确保至少生成了一个文档卡片
2. 检查浏览器下载设置
3. 查看浏览器控制台是否有错误

---

## 技术支持

如果遇到其他问题，请检查：

1. **后端日志：** 在运行 `uvicorn` 的终端查看
2. **前端控制台：** 打开浏览器开发者工具 Console 标签
3. **网络请求：** 开发者工具 Network 标签查看 API 请求
4. **单元测试：** 运行 pytest 查看具体失败原因

---

## 下一步

完成验收后，可以：
1. 尝试不同的课程主题和要求
2. 调整 UBD agent 的 prompt 以优化输出质量
3. 添加更多文档卡片样式
4. 实现协作编辑功能
5. 集成更多 AI 模型

---

**文档版本：** 1.0
**最后更新：** 2025-10-07
**作者：** Claude Code
