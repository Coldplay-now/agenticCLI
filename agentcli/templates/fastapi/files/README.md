# {{project_name}}

{{description}}

## 功能特点

- RESTful API 设计
- 自动 API 文档（Swagger UI / ReDoc）
- 数据库集成（SQLAlchemy）
- Docker 支持
- 完整的测试覆盖

## 技术栈

- **FastAPI**: 现代化、高性能的 Web 框架
- **SQLAlchemy**: Python SQL 工具包和 ORM
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI 服务器
- **Docker**: 容器化部署

## 快速开始

### 使用 Docker（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload

# 或
python -m app.main
```

访问 http://localhost:8000

## API 文档

启动服务后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 通用

- `GET /` - 根路径
- `GET /health` - 健康检查

### 项目管理

- `GET /api/v1/items` - 获取所有项目
- `GET /api/v1/items/{id}` - 获取单个项目
- `POST /api/v1/items` - 创建项目
- `PUT /api/v1/items/{id}` - 更新项目
- `DELETE /api/v1/items/{id}` - 删除项目

## 测试

```bash
# 安装测试依赖
pip install pytest pytest-cov httpx

# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app
```

## 项目结构

```
{{project_name}}/
├── app/
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py     # API 路由
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py     # 配置
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py     # 数据模型
│   └── db/
│       ├── __init__.py
│       └── database.py   # 数据库连接
├── tests/
│   ├── __init__.py
│   └── test_api.py       # API 测试
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 环境变量

复制 `.env.example` 到 `.env` 并配置：

```env
# 数据库 URL
DATABASE_URL=sqlite:///./{{project_name}}.db

# 调试模式
DEBUG=false
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t {{project_name}} .

# 运行容器
docker run -d -p 8000:8000 {{project_name}}
```

### 云平台部署

项目可以轻松部署到：
- AWS (ECS, Lambda)
- Google Cloud (Cloud Run)
- Azure (Container Instances)
- Heroku
- DigitalOcean

## 开发指南

### 添加新的 API 端点

1. 在 `app/api/routes.py` 中定义路由
2. 在 `app/models/` 中定义数据模型（如需要）
3. 在 `tests/test_api.py` 中添加测试

### 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head
```

## License

MIT License

## 作者

{{author_name}}

