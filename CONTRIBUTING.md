# 🤝 贡献指南 | Contributing Guide

感谢您对 PBLCourseAgent 项目的关注！我们欢迎所有形式的贡献。

Thank you for your interest in contributing to PBLCourseAgent! We welcome all forms of contributions.

## 🚀 快速开始 | Quick Start

### 环境准备 | Environment Setup

1. **Fork 项目 | Fork the Project**
   ```bash
   # 克隆你的 fork | Clone your fork
   git clone https://github.com/your-username/PBLCourseAgent.git
   cd PBLCourseAgent
   ```

2. **创建开发分支 | Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **设置开发环境 | Setup Development Environment**
   ```bash
   # 后端环境 | Backend Environment
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt

   # 前端环境 | Frontend Environment (Phase 2)
   cd frontend
   npm install
   ```

## 📝 贡献类型 | Types of Contributions

### 🐛 Bug 修复 | Bug Fixes
- 在 Issues 中报告问题
- 提供详细的重现步骤
- 包含系统环境信息

### ✨ 新功能 | New Features
- 先在 Issues 中讨论功能需求
- 确保符合项目路线图
- 提供详细的功能描述

### 📚 文档改进 | Documentation
- 修正错误或不清晰的描述
- 添加使用示例
- 翻译文档（中英文）

### 🧪 测试用例 | Test Cases
- 增加测试覆盖率
- 添加边界情况测试
- 性能测试优化

## 🔧 开发指南 | Development Guidelines

### 代码规范 | Code Standards

#### Python (后端 | Backend)
```bash
# 代码格式化 | Code Formatting
black .
isort .

# 代码检查 | Code Linting
flake8

# 测试 | Testing
pytest app/tests/ -v
```

#### TypeScript/React (前端 | Frontend - Phase 2)
```bash
# 代码格式化 | Code Formatting
npm run format

# 代码检查 | Code Linting
npm run lint

# 测试 | Testing
npm run test
```

### 提交规范 | Commit Convention

使用语义化提交信息 | Use semantic commit messages:

```
feat: 添加新功能 | add new feature
fix: 修复bug | fix bug
docs: 更新文档 | update documentation
style: 代码格式调整 | code style changes
refactor: 代码重构 | code refactoring
test: 添加测试 | add tests
chore: 构建过程或辅助工具的变动 | build process or auxiliary tool changes
```

示例 | Examples:
```bash
feat: 添加无限画布组件集成
fix: 修复AI Agent响应超时问题
docs: 更新API文档示例
```

## 🧪 测试指南 | Testing Guidelines

### 运行测试 | Running Tests

```bash
# 所有测试 | All Tests
pytest app/tests/ -v

# 特定模块 | Specific Module
pytest app/tests/test_workflow_service.py -v

# 覆盖率报告 | Coverage Report
pytest app/tests/ --cov=app --cov-report=html
```

### 添加测试 | Adding Tests

1. **单元测试 | Unit Tests**: 每个Agent和服务都应有对应测试
2. **集成测试 | Integration Tests**: 测试API端点和工作流
3. **性能测试 | Performance Tests**: 确保响应时间符合要求

## 📋 Pull Request 流程 | PR Process

### 提交前检查 | Pre-submission Checklist

- [ ] 代码通过所有测试
- [ ] 代码符合项目规范
- [ ] 添加了必要的测试用例
- [ ] 更新了相关文档
- [ ] 提交信息遵循规范

### PR 模板 | PR Template

```markdown
## 变更描述 | Description
简要描述你的变更内容

## 变更类型 | Type of Change
- [ ] Bug 修复 | Bug fix
- [ ] 新功能 | New feature
- [ ] 文档更新 | Documentation update
- [ ] 性能优化 | Performance improvement

## 测试 | Testing
- [ ] 添加了新的测试用例
- [ ] 所有测试通过
- [ ] 手动测试完成

## 截图 | Screenshots
如果有UI变更，请提供截图

## 相关Issue | Related Issues
关联相关的 Issue 编号
```

## 🌟 项目阶段 | Project Phases

### Phase 1: MVP (当前 | Current) ✅
- 专注于核心Agent功能改进
- 后端API优化
- 测试覆盖率提升

### Phase 2: Canvas Interface (开发中 | In Development) 🚧
- tldraw 无限画布集成
- React前端重构
- 节点-对话交互系统
- 状态管理架构

## 📞 获取帮助 | Getting Help

- **讨论 | Discussions**: [GitHub Discussions](https://github.com/username/PBLCourseAgent/discussions)
- **问题 | Issues**: [GitHub Issues](https://github.com/username/PBLCourseAgent/issues)
- **文档 | Documentation**: 查看 `docs/` 目录

## 🎉 贡献者认可 | Contributor Recognition

我们重视每一个贡献者的努力！贡献者将被：

We value every contributor's effort! Contributors will be:

- 列入项目贡献者名单 | Listed in project contributors
- 在 Release Notes 中致谢 | Acknowledged in release notes
- 获得项目贡献者徽章 | Receive contributor badges

## 📜 行为准则 | Code of Conduct

### 我们的承诺 | Our Pledge

为了营造一个开放和友好的环境，我们承诺让每个人都能参与到项目中来。

To foster an open and welcoming environment, we pledge to make participation in our project a harassment-free experience for everyone.

### 预期行为 | Expected Behavior

- 使用友好和包容的语言 | Use welcoming and inclusive language
- 尊重不同的观点和经验 | Respect differing viewpoints and experiences
- 优雅地接受建设性批评 | Accept constructive criticism gracefully
- 专注于对社区最有益的事情 | Focus on what is best for the community

---

**再次感谢您的贡献！Together, we're building the future of PBL course design! 🚀**