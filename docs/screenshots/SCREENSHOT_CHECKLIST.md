# 📸 产品截图清单

本文档提供了README.md所需的所有产品截图的详细说明。请按照以下顺序进行截图。

## 准备工作

1. **启动开发环境**
   ```bash
   # Terminal 1: 启动后端
   cd backend
   uv run uvicorn app.main:app --reload

   # Terminal 2: 启动前端
   cd frontend
   python -m http.server 3000
   ```

2. **准备示例数据**
   - 课程主题: `AI乐队制作人`
   - 课程概要: `学生将使用AI音乐生成工具创作原创歌曲，学习音乐制作、AI工具应用和创意表达`
   - 年龄段: `11-14岁`
   - 课程时长: `40课时（5天，每天半天）`
   - AI工具: `Suno AI, Claude AI, 音频编辑软件`

3. **浏览器设置**
   - 推荐使用Chrome或Edge浏览器
   - 分辨率: 1920x1080或更高
   - 缩放: 100%（避免显示模糊）

---

## 截图清单

### ✅ 截图1: 产品主界面
**文件名**: `main-interface.png`
**URL**: `http://localhost:3000`
**内容**:
- 完整的产品主界面
- 左侧输入表单区域（空白状态）
- 右侧输出展示区域（空白状态）
- 顶部标题和Logo

**截图步骤**:
1. 打开 http://localhost:3000
2. 不填写任何内容（保持初始状态）
3. 全屏截图 (F11或浏览器全屏)
4. 保存为 `docs/screenshots/main-interface.png`

**质量要求**:
- 分辨率: 1920x1080或更高
- 格式: PNG
- 文件大小: < 2MB

---

### ✅ 截图2: 课程生成进行中
**文件名**: `generation-in-progress.png`
**URL**: `http://localhost:3000`
**内容**:
- 左侧表单已填写完整
- 右侧正在显示流式生成的内容
- 能看到"正在生成项目基础定义..."或类似的进度提示

**截图步骤**:
1. 在左侧表单填写完整的示例数据（见准备工作）
2. 点击"生成课程方案"按钮
3. **快速准备截图工具**（因为是流式输出）
4. 在生成到一半时进行截图（最好是Stage 1正在生成时）
5. 保存为 `docs/screenshots/generation-in-progress.png`

**质量要求**:
- 分辨率: 1920x1080或更高
- 格式: PNG
- 捕捉到部分生成的内容，体现"流式"特性

---

### ✅ 截图3: 完整课程方案
**文件名**: `complete-course.png`
**URL**: `http://localhost:3000`
**内容**:
- 所有三个阶段都已生成完成
- 展示完整的输出结果
- 可以看到三个主要部分：项目基础定义、评估框架、学习蓝图

**截图步骤**:
1. 等待课程方案完全生成（约60-90秒）
2. 向下滚动到页面顶部，确保能看到所有三个部分的标题
3. 使用浏览器插件或工具进行**长截图**（推荐工具：GoFullPage、Awesome Screenshot）
4. 保存为 `docs/screenshots/complete-course.png`

**质量要求**:
- 格式: PNG
- 类型: 长截图（包含完整内容）
- 文件大小: < 5MB
- 清晰可读所有文字

---

### ✅ 截图4: 输入表单填写示例
**文件名**: `input-form.png`
**URL**: `http://localhost:3000`
**内容**:
- 聚焦左侧输入表单
- 所有字段已填写示例数据
- "生成课程方案"按钮清晰可见

**截图步骤**:
1. 打开 http://localhost:3000
2. 在左侧表单填写完整的示例数据
3. 使用截图工具框选**仅左侧表单区域**
4. 保存为 `docs/screenshots/input-form.png`

**质量要求**:
- 格式: PNG
- 类型: 局部截图（仅左侧表单）
- 宽度: 约600-800px
- 所有字段内容清晰可读

---

### ✅ 截图5: 项目基础定义部分
**文件名**: `stage1-foundation.png`
**URL**: `http://localhost:3000`（生成完成后）
**内容**:
- Agent 1生成的"项目基础定义"部分
- 包含驱动性问题、最终成果、学习目标等

**截图步骤**:
1. 完整生成一个课程方案
2. 滚动到"项目基础定义"部分的开头
3. 框选这一部分内容进行截图
4. 保存为 `docs/screenshots/stage1-foundation.png`

**质量要求**:
- 格式: PNG
- 类型: 局部截图
- 包含完整的Stage 1内容
- 文字清晰可读

---

### ✅ 截图6: 评估框架部分
**文件名**: `stage2-assessment.png`
**URL**: `http://localhost:3000`（生成完成后）
**内容**:
- Agent 2生成的"评估框架"部分
- 重点展示4级评估量规表格

**截图步骤**:
1. 完整生成一个课程方案
2. 滚动到"评估框架"部分
3. 确保完整的4级量规表格在视野内
4. 框选这一部分进行截图
5. 保存为 `docs/screenshots/stage2-assessment.png`

**质量要求**:
- 格式: PNG
- 类型: 局部截图
- 表格完整、清晰
- 所有评分级别可见

---

### ✅ 截图7: 学习蓝图部分
**文件名**: `stage3-blueprint.png`
**URL**: `http://localhost:3000`（生成完成后）
**内容**:
- Agent 3生成的"学习蓝图"部分
- 展示时间线和详细活动安排

**截图步骤**:
1. 完整生成一个课程方案
2. 滚动到"学习蓝图"部分
3. 捕捉教师准备清单和时间线内容
4. 框选进行截图
5. 保存为 `docs/screenshots/stage3-blueprint.png`

**质量要求**:
- 格式: PNG
- 类型: 局部截图
- 展示教学设计的完整性
- 时间线清晰可见

---

### ✅ 截图8: FastAPI交互式文档
**文件名**: `api-docs.png`
**URL**: `http://localhost:8000/docs`
**内容**:
- Swagger UI界面
- 所有API端点列表
- 特别突出 `/api/v1/generate/stream` 端点

**截图步骤**:
1. 确保后端已启动
2. 打开 http://localhost:8000/docs
3. 如果端点是折叠的，展开主要的端点（特别是 `/api/v1/generate/stream`）
4. 全屏截图
5. 保存为 `docs/screenshots/api-docs.png`

**质量要求**:
- 分辨率: 1920x1080或更高
- 格式: PNG
- 所有端点清晰可见
- Swagger UI主题和布局完整

---

### ✅ 截图9: 测试运行结果
**文件名**: `test-results.png`
**URL**: Terminal/命令行
**内容**:
- pytest运行的输出结果
- 显示所有测试PASSED状态
- 包含测试覆盖率统计（如果有）

**截图步骤**:
1. 打开终端（推荐使用Windows Terminal或iTerm2以获得更好的显示效果）
2. 运行测试命令:
   ```bash
   cd backend
   uv run pytest app/tests/ -v
   ```
3. 等待所有测试完成
4. 截取终端窗口（确保能看到完整的测试输出）
5. 保存为 `docs/screenshots/test-results.png`

**质量要求**:
- 分辨率: 1280x720或更高
- 格式: PNG
- 终端字体清晰可读
- 所有测试结果可见
- 最好使用有语法高亮的终端

---

## 截图工具推荐

### Windows
- **Snipping Tool** (内置，快捷键: Win+Shift+S)
- **ShareX** (免费，支持长截图)
- **Lightshot** (快速标注)

### macOS
- **Screenshot** (内置，快捷键: Cmd+Shift+4)
- **CleanShot X** (付费，功能强大)
- **Skitch** (免费，支持标注)

### 浏览器插件（跨平台）
- **GoFullPage** - Chrome/Edge插件，完美长截图
- **Awesome Screenshot** - 多功能截图和录屏
- **Fireshot** - 网页完整截图

---

## 图片优化

截图完成后，建议使用以下工具进行优化：

1. **TinyPNG** (https://tinypng.com/) - 在线压缩，保持质量
2. **ImageOptim** (macOS) - 本地无损压缩
3. **PNGGauntlet** (Windows) - 批量优化PNG

**优化目标**:
- 单张截图 < 2MB（长截图可放宽到5MB）
- 保持文字清晰可读
- 删除EXIF元数据

---

## 完成清单

在完成所有截图后，请检查：

- [ ] 所有9张截图都已保存到 `docs/screenshots/` 目录
- [ ] 文件名与上述清单完全一致
- [ ] 所有截图格式为PNG
- [ ] 文字清晰可读（特别是代码和表格）
- [ ] 文件大小符合要求
- [ ] 在README.md中能正确显示所有图片

---

## 验证显示效果

完成截图后，在本地验证README中的图片显示：

```bash
# 使用Markdown预览工具
# 推荐: VS Code + Markdown Preview Enhanced插件
# 或者将README推送到GitHub查看效果
```

---

**完成后，您的README.md将拥有完整的视觉呈现，大大提升项目的专业度和可理解性！** 📸✨
