# 🚀 UV 使用指南

## 什么是 uv？

[uv](https://docs.astral.sh/uv/) 是一个现代、快速的Python包管理器，由Astral公司开发。它比传统的pip + virtualenv组合快10-100倍。

## 🔧 安装 uv

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 验证安装
```bash
uv --version
```

## 📦 在本项目中使用 uv

### 首次设置
```bash
cd backend
uv sync  # 读取pyproject.toml并安装所有依赖
```

### 日常开发命令

#### 环境管理
```bash
# 查看虚拟环境信息
uv info

# 进入虚拟环境shell
uv shell

# 退出虚拟环境
exit
```

#### 运行命令
```bash
# 在uv环境中运行Python脚本
uv run python script.py

# 启动FastAPI服务
uv run uvicorn app.main:app --reload

# 运行测试
uv run pytest app/tests/ -v

# 运行代码格式化
uv run black .
uv run isort .
uv run flake8
```

#### 依赖管理
```bash
# 添加生产依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name

# 移除依赖
uv remove package_name

# 更新所有依赖
uv sync --upgrade

# 更新特定依赖
uv add package_name@latest
```

#### 查看依赖
```bash
# 查看已安装的包
uv pip list

# 查看依赖树
uv pip show package_name

# 导出requirements.txt
uv export --format requirements-txt --output requirements.txt
```

## 🔄 从 pip 迁移到 uv

### 传统方式 vs uv方式

| 传统方式 | uv方式 | 说明 |
|---------|-------|------|
| `python -m venv venv` | `uv sync` | 创建虚拟环境 |
| `source venv/bin/activate` | `uv shell` | 激活环境 |
| `pip install package` | `uv add package` | 安装包 |
| `pip install -r requirements.txt` | `uv sync` | 安装依赖 |
| `python script.py` | `uv run python script.py` | 运行脚本 |

### 优势对比

- **速度**: uv比pip快10-100倍
- **一致性**: 使用lock文件确保依赖版本一致
- **简化**: 不需要手动管理虚拟环境
- **现代**: 支持最新的Python打包标准

## 🛠️ 项目开发工作流

### 1. 初始设置
```bash
# 克隆项目
git clone <repo>
cd eduagents/backend

# 安装uv（如果还没有）
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 设置项目环境
uv sync
```

### 2. 开发过程
```bash
# 启动开发服务器
uv run uvicorn app.main:app --reload

# 运行测试
uv run pytest

# 添加新依赖
uv add requests

# 代码质量检查
uv run black . && uv run isort . && uv run flake8
```

### 3. 提交代码
```bash
# 确保测试通过
uv run pytest

# 格式化代码
uv run black .
uv run isort .

# 提交更改（pyproject.toml和uv.lock都会被包含）
git add .
git commit -m "your changes"
```

## 📁 重要文件说明

- **`pyproject.toml`**: 项目配置，包含依赖声明和工具配置
- **`uv.lock`**: 锁定文件，确保依赖版本一致性（应该提交到git）
- **`.python-version`**: 指定Python版本

## 🔍 故障排除

### 常见问题

1. **uv command not found**
   ```bash
   # 重新安装uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # 重启终端
   ```

2. **Python版本不匹配**
   ```bash
   # 检查Python版本
   python --version
   # 应该是3.9+
   ```

3. **依赖冲突**
   ```bash
   # 清理并重新安装
   rm -rf .venv uv.lock
   uv sync
   ```

4. **权限问题**
   ```bash
   # 确保有写入权限
   chmod +w pyproject.toml
   ```

## 🚀 高级用法

### 多Python版本管理
```bash
# 指定Python版本
uv venv --python 3.9

# 使用特定版本
uv run --python 3.11 python script.py
```

### 工作空间管理
```bash
# 为不同环境创建不同配置
uv add --dev pytest-cov  # 开发环境
uv add requests          # 生产环境
```

### 性能优化
```bash
# 使用缓存加速安装
uv sync --cache-dir ~/.uv/cache

# 并行安装
uv sync --concurrent-downloads 10
```

## 💡 最佳实践

1. **始终提交 uv.lock**: 确保团队环境一致
2. **使用 uv run**: 避免手动激活虚拟环境
3. **定期更新**: 使用 `uv sync --upgrade` 更新依赖
4. **分离依赖**: 生产依赖和开发依赖分开管理
5. **版本固定**: 重要依赖固定版本号

## 📚 更多资源

- [uv官方文档](https://docs.astral.sh/uv/)
- [uv GitHub仓库](https://github.com/astral-sh/uv)
- [Python打包用户指南](https://packaging.python.org/)