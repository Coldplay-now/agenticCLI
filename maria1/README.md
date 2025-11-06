# maria1

命令行版超级玛丽游戏 - 在终端中体验经典平台跳跃冒险

## 功能特点

- 功能1：[描述]
- 功能2：[描述]
- 功能3：[描述]

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd maria1

# 安装依赖
pip install -r requirements.txt

# 安装为可执行程序（推荐，支持 python -m maria1 运行）
pip install -e .
```

**注意**：如果使用 `python -m maria1` 运行，必须先执行 `pip install -e .` 安装包。

## 使用方法

### 基本用法

```bash
# 运行主程序
python -m maria1 run

# 查看帮助
python -m maria1 --help

# 查看版本信息
python -m maria1 info
```

### 高级用法

```bash
# 启用详细输出
python -m maria1 run --verbose
```

## 开发

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=maria1
```

### 代码规范

项目遵循 PEP 8 编码规范。

```bash
# 安装代码检查工具
pip install flake8 black

# 检查代码
flake8 maria1

# 格式化代码
black maria1
```

## 项目结构

```
maria1/
├── maria1/     # 主包
│   ├── __init__.py
│   ├── cli.py          # CLI 接口
│   └── core.py         # 核心逻辑
├── tests/              # 测试
│   ├── __init__.py
│   └── test_core.py
├── README.md           # 项目文档
├── requirements.txt    # 依赖
├── setup.py           # 安装配置
└── .gitignore         # Git 忽略文件
```

## License

MIT License

## 贡献

欢迎贡献！请提交 Pull Request。

## 作者

开发者

