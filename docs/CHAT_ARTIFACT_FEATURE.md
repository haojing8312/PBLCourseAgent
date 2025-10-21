# 对话驱动的课程方案修改功能 (Chat Artifact Feature)

## 功能概述

此功能实现了类似ChatGPT Canvas的体验：当用户在左侧对话区域要求修改课程方案时，AI会自动在右侧区域重新生成对应的Stage内容。

### 用户体验流程

```
用户在对话框输入："把学习目标改成培养批判性思维"
         ↓
AI在对话区回复："好的，我将重新生成Stage 1..."
         ↓
自动切换到右侧Stage 1标签页
         ↓
右侧Markdown内容开始重新生成
         ↓
生成完成后，右侧显示更新后的课程方案
```

## 技术架构

### 整体数据流

```
前端ChatPanel
    ↓ [用户消息]
useChatConversation
    ↓ [SSE流式请求]
后端Chat API (/api/v1/chat/stream)
    ↓ [调用]
CourseChatAgent
    ↓ [AI识别修改意图，在回复中添加REGENERATE标记]
Chat API解析标记
    ↓ [发送artifact事件]
前端chatService
    ↓ [onArtifact回调]
useChatConversation
    ↓ [onRegenerateRequest回调]
App.tsx的handleRegenerateFromChat
    ↓ [切换步骤 + 调用WorkflowService]
重新生成Stage内容
    ↓ [更新Store]
右侧ContentPanel自动刷新
```

## 关键实现

### 1. 后端：AI意图识别

**文件**: `backend/app/agents/course_chat_agent.py`

AI的system prompt中添加了明确的指令：

```python
"""
【重要】当用户明确要求修改课程方案时，你需要触发重新生成：
1. 在回复的**第一行**添加特殊标记：[REGENERATE:STAGE_X:修改说明]
   - X是阶段编号（1/2/3）
   - 修改说明是对用户需求的简洁总结（不超过50字）

2. 然后在第二行开始正常回复用户，解释你的修改思路

判断标准：
- 需要REGENERATE：用户说"修改"、"改成"、"改为"、"调整"、"优化"、"重新生成"课程方案的具体内容
- 不需要REGENERATE：用户只是咨询、询问、解释、讨论

示例（需要重新生成）：
用户："把学习目标改成培养批判性思维"
你的回复：
[REGENERATE:STAGE_1:将学习目标重点调整为培养批判性思维能力]
好的，我将重新生成Stage 1...
"""
```

### 2. 后端：Artifact事件生成

**文件**: `backend/app/api/v1/chat.py`

Chat API在流式输出过程中：
1. 累积完整的AI回复
2. 使用正则表达式检测REGENERATE标记
3. 如果检测到，发送artifact事件（SSE格式）

```python
# 检测REGENERATE标记
regenerate_match = re.match(r'\[REGENERATE:STAGE_(\d+):(.*?)\]', full_response)

if regenerate_match:
    stage = int(regenerate_match.group(1))
    instructions = regenerate_match.group(2).strip()

    # 发送artifact事件
    artifact_event = {
        'type': 'artifact',
        'action': 'regenerate',
        'stage': stage,
        'instructions': instructions
    }
    yield f"data: {json.dumps(artifact_event, ensure_ascii=False)}\n\n"
```

### 3. 前端：SSE事件处理

**文件**: `frontend-x/src/services/chatService.ts`

扩展了SSE事件类型和处理器：

```typescript
export interface ChatStreamEvent {
  type: 'start' | 'chunk' | 'done' | 'error' | 'artifact';
  // Artifact事件专用字段
  action?: 'regenerate';
  stage?: number;
  instructions?: string;
}

export interface ChatStreamHandlers {
  onStart?: () => void;
  onChunk?: (content: string) => void;
  onDone?: () => void;
  onError?: (error: string) => void;
  onArtifact?: (artifact: { action: string; stage: number; instructions: string }) => void;
}
```

### 4. 前端：回调传递链

**文件链**:
1. `App.tsx`: 定义 `handleRegenerateFromChat`
2. `ChatPanel.tsx`: 接收并传递 `onRegenerateRequest`
3. `useChatConversation.ts`: 接收并在`onArtifact`中调用

```typescript
// App.tsx
const handleRegenerateFromChat = async (stage: number, instructions: string) => {
  // 1. 显示提示
  message.info(`AI正在根据您的要求重新生成 Stage ${stage}...`);

  // 2. 切换到对应阶段
  if (currentStep !== stage) {
    useCourseStore.getState().setCurrentStep(stage);
  }

  // 3. 触发重新生成
  await handleGenerateStage(stage);
};

// 传递给ChatPanel
<ChatPanel
  currentStep={currentStep}
  courseId={courseInfo?.id}
  onRegenerateRequest={handleRegenerateFromChat}
/>
```

## 测试验证

### 单元测试

**文件**: `backend/app/tests/test_chat_artifact.py`

测试覆盖：
- ✅ REGENERATE标记的正则表达式匹配
- ✅ 不同Stage的识别
- ✅ 特殊字符处理
- ✅ artifact事件的JSON格式
- ✅ SSE格式验证

运行测试：
```bash
cd backend
python -m pytest app/tests/test_chat_artifact.py -v
```

### 集成测试

**文件**: `backend/test_artifact_integration.py`

测试流程：
1. 创建测试课程
2. 发送修改请求："把学习目标改成培养批判性思维"
3. 验证AI回复中包含REGENERATE标记
4. 验证收到正确的artifact事件

运行测试：
```bash
cd backend
python test_artifact_integration.py
```

测试结果示例：
```
✅ 测试通过：成功检测到artifact事件
   Stage: 1
   Instructions: 将学习目标从掌握Python基础调整为培养批判性思维
```

## 使用方法

### 对于用户

1. 打开课程设计界面
2. 在左侧对话框中输入修改请求，例如：
   - "把学习目标改成培养批判性思维"
   - "调整评估量规，增加更多案例"
   - "优化学习活动，增加小组合作环节"
3. AI会识别您的意图，并自动：
   - 在对话中确认理解
   - 切换到对应的Stage标签页
   - 重新生成课程方案

### 对于开发者

#### 扩展AI的识别能力

编辑 `backend/app/agents/course_chat_agent.py` 中的 `_build_system_prompt()` 方法，调整判断标准和示例。

#### 自定义artifact处理逻辑

编辑 `frontend-x/src/App.tsx` 中的 `handleRegenerateFromChat()` 方法。

当前实现是重新生成整个Stage，未来可以扩展为：
- 局部修改（根据instructions只修改特定字段）
- 增量更新（在现有内容基础上追加）
- 多轮refinement（记住修改历史）

## 已知限制与未来改进

### 当前限制

1. **整体重新生成**：目前只能重新生成整个Stage，无法局部修改
2. **instructions未完全利用**：修改说明只是传递给后端，但Agent并未根据它进行定向修改
3. **无历史记录**：无法查看修改历史或撤销

### 未来改进方向

1. **支持局部修改**
   ```typescript
   // 未来可以支持更细粒度的修改
   {
     action: 'update_field',
     stage: 1,
     field: 'understandings',  // 只修改U部分
     instructions: '调整为批判性思维'
   }
   ```

2. **修改历史记录**
   - 存储每次修改前的版本
   - 提供撤销/重做功能
   - 显示修改对比

3. **智能Diff显示**
   - 高亮显示修改的部分
   - 提供接受/拒绝修改的按钮

4. **多轮refinement**
   - AI记住修改历史
   - 支持增量调整

## 文件清单

### 后端文件

- `backend/app/agents/course_chat_agent.py` - 增强AI prompt
- `backend/app/api/v1/chat.py` - 解析REGENERATE标记，发送artifact事件
- `backend/app/tests/test_chat_artifact.py` - 单元测试
- `backend/test_artifact_integration.py` - 集成测试

### 前端文件

- `frontend-x/src/services/chatService.ts` - 扩展SSE事件类型和处理
- `frontend-x/src/hooks/useChatConversation.ts` - 添加onRegenerateRequest回调
- `frontend-x/src/components/ChatPanel.tsx` - 传递regenerate回调
- `frontend-x/src/App.tsx` - 实现handleRegenerateFromChat函数

## 贡献者

本功能由Anthropic的Claude Code助手（Sonnet 4.5）与用户协作完成。

## 更新日志

### v1.0 (2025-10-21)
- ✅ 实现基础的artifact事件机制
- ✅ AI能识别修改意图并触发重新生成
- ✅ 前端自动切换到对应Stage并更新内容
- ✅ 完整的单元测试和集成测试
