# AgentCLI 快速开始指南

## 第一步：安装依赖

```bash
# 确保使用 Python 3.10+
python --version

# 安装依赖
pip install -r requirements.txt
```

## 第二步：配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

## 第三步：验证配置

```bash
# 运行环境检查
python -m agentcli.main doctor
```

如果所有检查通过，你就可以开始使用了！

## 第四步：创建你的第一个项目

**重要：必须在项目根目录（1106-AgentCli）下运行！**

```bash
# 确保在项目根目录
cd /Users/xt/LXT/code/trae/1106-AgentCli

# 运行 AgentCLI
python -m agentcli

# 或者安装后可以在任何地方运行
pip install -e .
agentcli
```

按照提示回答问题即可！

### 方式一：直接运行（推荐开发时使用）

```bash
# 在项目根目录下
cd /path/to/1106-AgentCli
python -m agentcli
```

### 方式二：安装为可执行程序（推荐生产使用）

```bash
# 在项目根目录下安装
cd /path/to/1106-AgentCli
pip install -e .

# 安装后可以在任何目录运行
agentcli
```

## 示例：创建 Python CLI 工具

```bash
$ python -m agentcli

# 选择项目类型
请问你想创建什么类型的项目？
A) Python CLI 工具
B) Python Web API (FastAPI)
> A

# 描述项目用途
这个Python CLI 工具的主要用途是什么？
> 文件批量重命名工具

# 输入项目名称
请输入项目名称（用于创建目录）
> file-renamer

# AI 分析并生成任务清单...
# 确认后自动创建项目
```

## 示例：创建 FastAPI 项目

```bash
$ python -m agentcli

# 选择项目类型
> B

# 描述项目用途
> 博客后端 API

# 选择数据库
需要数据库支持吗？
> A  # SQLite

# 选择 Docker
需要 Docker 配置吗？
> A  # 需要

# 输入项目名称
> blog-api

# 确认任务清单后自动创建
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_file_ops.py

# 查看测试覆盖率
pytest --cov=agentcli
```

## 常见问题

### 1. No module named agentcli

**错误信息**:
```
No module named agentcli
```

**原因**: 在错误的目录下运行命令

**解决方法**:
```bash
# 确保在项目根目录（1106-AgentCli）下运行
cd /path/to/1106-AgentCli
python -m agentcli

# 或者安装为可执行程序
pip install -e .
agentcli  # 安装后可以在任何目录运行
```

### 2. API Key 无效

确保在 `.env` 文件中设置了正确的 DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=sk-your-actual-key-here
```

### 3. 找不到 systemprompt.md

确保 `systemprompt.md` 文件在项目根目录下。

### 4. 模板文件缺失

确保 `agentcli/templates/` 目录下有完整的模板文件。

### 5. 网络连接问题

如果无法连接 DeepSeek API，检查：
- 网络连接是否正常
- API 服务是否可用
- 是否需要配置代理

## 下一步

- 查看 [README.md](README.md) 了解更多功能
- 阅读 [PRD](PRD_AgentCLI_v0.1.0.md) 了解设计细节
- 查看生成的项目，学习项目结构
- 自定义模板以适应你的需求

## 获取帮助

```bash
# 查看帮助信息
python -m agentcli --help

# 查看版本
python -m agentcli --version

# 运行环境诊断
python -m agentcli.main doctor
```

祝你使用愉快！ 🎉

