# AgentCLI - 智能项目初始化助手

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)
![AI Powered](https://img.shields.io/badge/AI-DeepSeek-yellow.svg)
![CLI](https://img.shields.io/badge/CLI-Click-orange.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

一个智能化的 CLI Agent 工具，通过自然语言交互和 AI 推理能力，帮助开发者快速创建规范、完整的项目脚手架。

## 界面预览

### 启动界面
![启动界面](pic/20251106-163024.jpg)

### AI 推理过程（流式输出）
![AI 推理过程](pic/20251106-163040.jpg)

### 任务执行与项目创建
![任务执行](pic/20251106-163045.jpg)

## 功能特点

- **多轮对话交互**: 通过友好的对话方式收集项目需求
- **流式输出反馈**: AI 响应实时流式显示，提供更好的交互体验
- **CoT 推理分析**: 使用 Chain of Thought 推理分析用户需求并推荐最佳技术选型
- **智能任务生成**: 自动生成结构化的任务清单（≤10项）
- **自动化执行**: 按顺序自动执行任务，创建完整的项目结构
- **项目模板**: 
  - Python CLI 工具模板
  - FastAPI Web 项目模板

## 安装

### 前置要求

- Python 3.10+
- DeepSeek API Key

### 安装步骤

1. 克隆仓库：
```bash
git clone <repository-url>
cd 1106-AgentCli
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key
```

5. 安装 AgentCLI（可选）：
```bash
pip install -e .
```

## 使用方法

### 基本使用

```bash
python -m agentcli
```

或者如果已安装：

```bash
agentcli
```

### 使用流程

1. 启动 AgentCLI
2. 回答一系列关于项目的问题
3. AI 会分析你的需求并生成任务清单
4. 确认任务清单后，自动创建项目
5. 根据提示进入项目目录开始开发

### 示例场景

**创建 Python CLI 工具：**

```bash
$ python -m agentcli

请问你想创建什么类型的项目？
A) Python CLI 工具
B) Python Web API (FastAPI)

> A

请描述一下这个CLI工具的主要功能？
> 文件批量重命名工具

[AI 分析并生成任务清单...]
[自动创建项目...]

项目创建成功！
```

**创建 FastAPI 项目：**

```bash
$ python -m agentcli

请问你想创建什么类型的项目？
A) Python CLI 工具
B) Python Web API (FastAPI)

> B

这个API项目的主要用途是什么？
> 博客后端服务

[AI 分析并生成任务清单...]
[自动创建项目...]

项目创建成功！
```

## 项目结构

```
1106-AgentCli/
├── agentcli/              # 主包
│   ├── __init__.py
│   ├── main.py            # CLI 入口
│   ├── config.py          # 配置管理
│   ├── ai_client.py       # DeepSeek API 客户端
│   ├── conversation.py    # 对话管理
│   ├── task_generator.py  # 任务生成器
│   ├── task_executor.py   # 任务执行引擎
│   ├── templates/         # 项目模板
│   │   ├── python_cli/
│   │   └── fastapi/
│   └── utils/             # 工具函数
│       ├── file_ops.py
│       └── template_loader.py
├── tests/                 # 测试
├── systemprompt.md        # 系统提示词
├── requirements.txt       # 依赖
├── setup.py              # 安装配置
├── .env.example          # 环境变量示例
└── README.md             # 项目文档
```

## 运作机制

AgentCLI 通过多个核心组件协同工作，实现从用户需求到项目创建的完整流程。

### 系统架构拓扑图

以下图表展示了各个组件之间的关系和数据流向：

```mermaid
graph TB
    subgraph "用户交互层"
        User[用户]
        CLI[CLI 入口<br/>main.py]
    end
    
    subgraph "核心业务层"
        Conv[对话管理器<br/>ConversationManager]
        TG[任务生成器<br/>TaskGenerator]
        TE[任务执行器<br/>TaskExecutor]
    end
    
    subgraph "AI 服务层"
        AIClient[AI 客户端<br/>AIClient]
        LLM[DeepSeek API<br/>LLM]
    end
    
    subgraph "配置与资源"
        Config[配置管理<br/>Config]
        SystemPrompt[系统提示词<br/>systemprompt.md]
        Templates[项目模板<br/>templates/]
        Env[环境变量<br/>.env]
    end
    
    subgraph "输出结果"
        TaskList[任务清单<br/>TaskList]
        UserProject[用户项目<br/>生成的项目]
    end
    
    User -->|输入需求| CLI
    CLI -->|启动流程| Conv
    CLI -->|加载配置| Config
    Config -->|读取| Env
    Config -->|加载| SystemPrompt
    
    Conv -->|收集需求| User
    Conv -->|对话历史| AIClient
    AIClient -->|API 调用| LLM
    LLM -->|AI 响应| AIClient
    SystemPrompt -->|指导| LLM
    
    Conv -->|需求信息| TG
    TG -->|生成任务请求| AIClient
    AIClient -->|CoT 推理| LLM
    LLM -->|任务清单 JSON| TG
    TG -->|解析验证| TaskList
    
    TaskList -->|任务列表| TE
    TE -->|加载模板| Templates
    TE -->|执行任务| UserProject
    
    style User fill:#e1f5fe
    style UserProject fill:#c8e6c9
    style LLM fill:#fff9c4
    style SystemPrompt fill:#f3e5f5
    style Templates fill:#e8f5e9
```

### 完整流程时序图

以下时序图展示了从用户启动到项目创建的完整执行流程：

```mermaid
sequenceDiagram
    participant User as 用户
    participant CLI as CLI 入口
    participant Config as 配置管理
    participant Conv as 对话管理器
    participant AIClient as AI 客户端
    participant LLM as DeepSeek API
    participant TG as 任务生成器
    participant TE as 任务执行器
    participant Templates as 模板系统
    participant FS as 文件系统
    
    User->>CLI: 启动 agentcli
    CLI->>Config: 加载配置
    Config->>Config: 读取 .env (API Key)
    Config->>Config: 加载 systemprompt.md
    Config-->>CLI: 返回配置对象
    
    CLI->>AIClient: 初始化 AI 客户端
    AIClient-->>CLI: 客户端就绪
    
    CLI->>Conv: 创建对话管理器
    Conv-->>CLI: 管理器就绪
    
    Note over User,Conv: 阶段 1: 需求收集
    loop 多轮对话
        Conv->>User: 提问（项目类型/用途等）
        User->>Conv: 回答
        Conv->>Conv: 记录对话历史
    end
    
    Conv->>Conv: 验证需求完整性
    Conv-->>CLI: 需求收集完成
    
    Note over CLI,LLM: 阶段 2: AI 推理与任务生成
    CLI->>TG: 创建任务生成器
    TG->>AIClient: 请求生成任务清单
    AIClient->>LLM: 发送 CoT 推理请求<br/>（包含需求+系统提示词）
    
    Note over LLM: CoT 推理过程:<br/>1. 需求理解<br/>2. 技术选型<br/>3. 项目结构<br/>4. 任务分解
    
    LLM-->>AIClient: 流式返回推理过程+任务清单 JSON
    AIClient-->>TG: 返回完整响应
    
    TG->>TG: 提取 JSON<br/>解析任务清单
    TG->>TG: 验证任务格式<br/>（数量≤10，类型正确）
    TG-->>CLI: 返回 TaskList 对象
    
    CLI->>User: 展示任务清单
    User->>CLI: 确认执行
    
    Note over CLI,FS: 阶段 3: 任务执行
    CLI->>TE: 创建任务执行器
    TE->>TE: 设置项目变量
    
    loop 执行每个任务
        TE->>TE: 判断任务类型
        
        alt 创建目录
            TE->>FS: create_directory()
        else 创建文件
            alt 使用模板
                TE->>Templates: 加载模板文件
                Templates-->>TE: 返回模板内容
                TE->>TE: 替换变量
            else 使用 content
                TE->>TE: 直接使用 content
            end
            TE->>FS: create_file()
        else 执行命令
            TE->>FS: execute_command()
        end
        
        TE->>TE: 记录执行结果
    end
    
    TE-->>CLI: 所有任务完成
    CLI->>User: 显示项目创建成功<br/>提供后续指引
    
    Note over User,FS: 结果: 用户获得完整的项目
```

### 核心组件说明

#### 1. 对话管理器 (ConversationManager)
- **职责**: 管理多轮对话，收集用户需求
- **输入**: 用户回答
- **输出**: 需求字典、对话历史
- **特点**: 每次只问一个问题，提供 A/B/C 选择

#### 2. 任务生成器 (TaskGenerator)
- **职责**: 基于 AI 推理生成任务清单
- **输入**: 需求信息、对话历史
- **输出**: TaskList 对象（包含 ≤10 个任务）
- **特点**: 使用 CoT 推理，生成结构化的 JSON 任务清单

#### 3. 任务执行器 (TaskExecutor)
- **职责**: 执行任务清单，创建项目文件
- **输入**: TaskList 对象
- **输出**: 完整的项目目录和文件
- **特点**: 支持三种任务类型，自动变量替换，实时进度显示

#### 4. AI 客户端 (AIClient)
- **职责**: 封装 DeepSeek API 调用
- **输入**: 消息列表、系统提示词
- **输出**: AI 响应（支持流式输出）
- **特点**: 自动重试、错误处理、流式显示

#### 5. 模板系统 (Templates)
- **职责**: 提供项目模板文件
- **位置**: `agentcli/templates/`
- **内容**: Python CLI 和 FastAPI 项目模板
- **特点**: 支持变量替换，可扩展

#### 6. 系统提示词 (systemprompt.md)
- **职责**: 指导 AI 的行为和输出格式
- **内容**: 角色定义、工作流程、任务格式要求
- **特点**: 可配置，影响 AI 的推理和代码生成质量

### 数据流向

1. **需求收集阶段**:
   ```
   用户输入 → ConversationManager → 需求字典
   ```

2. **任务生成阶段**:
   ```
   需求字典 + 对话历史 → TaskGenerator → AIClient → DeepSeek API
   → CoT 推理 → JSON 任务清单 → TaskList 对象
   ```

3. **任务执行阶段**:
   ```
   TaskList → TaskExecutor → 模板系统/直接内容 → 文件系统 → 用户项目
   ```

### 关键设计决策

- **流式输出**: AI 响应实时显示，提升用户体验
- **变量自动替换**: 确保所有模板变量被正确替换
- **代码生成**: AI 直接生成实际功能代码，而非仅使用模板
- **任务限制**: 最多 10 个任务，保持清单简洁
- **错误处理**: 每个环节都有完善的错误处理和用户提示

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码规范

项目遵循 PEP 8 编码规范。

## 技术栈

- **Python 3.10+**: 主要开发语言
- **DeepSeek API**: AI 推理和对话
- **Click**: CLI 框架
- **Rich**: 命令行美化
- **Pydantic**: 数据验证

## License

MIT License

## 贡献

欢迎贡献！请查看贡献指南。

## 支持

如有问题，请提交 Issue。

