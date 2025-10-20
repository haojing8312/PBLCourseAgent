# Prompt管理目录

## 目录结构

```
prompts/
├── README.md           # 本文件：Prompt管理说明
├── phr/                # Prompt History Records（提示词历史记录）
│   ├── project_foundation_v1.md
│   ├── assessment_framework_v1.md
│   └── learning_blueprint_v1.md
└── schemas/            # JSON Schema定义（未来使用）
    └── (待添加)
```

---

## Prompt History Record (PHR) 格式规范

每个Agent的Prompt应该独立维护在PHR文件中，遵循以下格式：

### 文件命名规范

```
{agent_name}_{version}.md
```

例如：
- `project_foundation_v1.md` - ProjectFoundationAgent的v1版本
- `project_foundation_v2.md` - ProjectFoundationAgent的v2版本

### PHR文件结构

```markdown
# Prompt History Record: {Agent Name} v{X.Y}

## Meta Information
- **Version**: vX.Y
- **Created**: YYYY-MM-DD
- **Last Modified**: YYYY-MM-DD
- **Model**: 使用的LLM模型（如 deepseek-chat）
- **Performance Metrics**:
  - Average Response Time: XXs
  - Success Rate: XX%
  - Quality Score: X.X/10 (基于测试案例)

## System Prompt

[完整的System Prompt内容]

## Guidelines for Use

[使用指南和注意事项]

## Change Log

### v1.0 (YYYY-MM-DD)
- 初始版本
- 描述：[版本特性描述]

### v1.1 (YYYY-MM-DD)
- 修改：[具体修改内容]
- 原因：[修改原因]
- 影响：[对输出的影响]

## Known Issues

[已知问题和局限性]

## Testing Notes

[测试结果和优化建议]
```

---

## Prompt版本管理原则

### 1. 不要直接修改现有版本

**错误做法** ❌:
```bash
# 直接修改v1文件
vim phr/project_foundation_v1.md
```

**正确做法** ✅:
```bash
# 创建新版本
cp phr/project_foundation_v1.md phr/project_foundation_v2.md
# 然后修改v2
```

### 2. 每次修改都要记录Change Log

**错误做法** ❌:
- 修改Prompt但不记录原因
- 删除旧的Change Log条目

**正确做法** ✅:
- 在Change Log中添加新条目
- 说明：修改了什么、为什么修改、预期影响

### 3. 记录性能指标

每个版本应该记录：
- 平均响应时间
- 成功率（无JSON解析错误的比例）
- 质量评分（基于测试案例或人工评估）

这些指标用于版本间的对比和决策。

### 4. 运行回归测试

修改Prompt后，**必须**运行测试：

```bash
cd backend
uv run pytest app/tests/test_{agent_name}.py -v
```

### 5. 更新Agent代码引用

如果决定使用新版本Prompt，需要：

1. 修改Agent代码中的Prompt加载逻辑
2. 或保留硬编码Prompt但添加注释指向PHR文件

---

## 如何添加新Agent的Prompt

### 步骤1: 创建PHR文件

```bash
touch backend/app/prompts/phr/{new_agent_name}_v1.md
```

### 步骤2: 填写PHR内容

参考现有的PHR文件（如 `project_foundation_v1.md`），填写完整的Meta信息和System Prompt。

### 步骤3: 在Agent代码中引用

方式1（当前方式）：硬编码在Agent类中
```python
def _build_system_prompt(self) -> str:
    """构建系统提示词

    Prompt版本: 参见 backend/app/prompts/phr/{agent_name}_v1.md
    """
    return """
    [Prompt内容]
    """
```

方式2（推荐方式）：从文件加载
```python
import os

def _build_system_prompt(self) -> str:
    """构建系统提示词"""
    phr_path = os.path.join(
        os.path.dirname(__file__),
        "../prompts/phr/project_foundation_v1.md"
    )
    with open(phr_path, 'r', encoding='utf-8') as f:
        # 解析Markdown，提取System Prompt部分
        content = f.read()
        # [解析逻辑]
    return prompt
```

### 步骤4: 添加到AGENTS.md

在 `AGENTS.md` 中添加新Agent的文档说明，包括Prompt版本引用。

---

## Prompt A/B测试

### 场景
你想测试两个不同的Prompt，看哪个效果更好。

### 步骤

1. **创建两个版本**:
   - `project_foundation_v2_variant_a.md`
   - `project_foundation_v2_variant_b.md`

2. **运行对比测试**:
   ```bash
   # 使用Variant A运行测试
   # [修改Agent代码临时使用Variant A]
   uv run pytest app/tests/ -v > results_variant_a.txt

   # 使用Variant B运行测试
   # [修改Agent代码临时使用Variant B]
   uv run pytest app/tests/ -v > results_variant_b.txt
   ```

3. **对比结果**:
   - 响应时间
   - 成功率
   - 输出质量（人工评估或自动化评分）

4. **选择获胜者**:
   - 将获胜的Variant重命名为 `v2.md`
   - 在Change Log中记录测试结果和选择原因

---

## 常见问题

### Q: 为什么要单独管理Prompt？

A: Prompt是Agent的核心逻辑，应该像代码一样进行版本控制和测试。单独管理的好处：
- 便于版本对比
- 记录优化历史
- 支持A/B测试
- 避免意外修改

### Q: 何时应该创建新版本？

A: 以下情况应该创建新版本：
- 修改Prompt的核心逻辑或结构
- 添加/删除重要的指令
- 修改输出Schema
- 调整温度、Token等关键参数

小的格式调整可以直接修改并在Change Log中记录。

### Q: 如何回滚到旧版本？

A:
1. 找到旧版本的PHR文件（如 `v1.md`）
2. 修改Agent代码引用该版本
3. 运行测试确保兼容性
4. 在当前版本的Change Log中记录回滚原因

### Q: PHR文件可以删除吗？

A: 不建议删除。保留旧版本的好处：
- 作为历史参考
- 可能需要回滚
- 对比不同版本的效果

如果确实要删除，至少保留Change Log信息。

---

## 相关资源

- [Spec-Kit-Plus PHR概念](https://github.com/panaversity/spec-kit-plus)
- [AGENTS.md](../../AGENTS.md) - Agent架构文档
- [CLAUDE.md](../../CLAUDE.md) - 开发规范

---

## 维护日志

- 2025-01-20: 创建Prompt管理目录和规范文档
