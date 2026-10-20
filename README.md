# Service Desk Copilot

一个面向企业客户支持场景的 AI Agent 工程项目。系统使用 FastAPI 提供客户、工单、会话和消息 API，并通过大模型 Tool Calling 完成业务查询、工单检查与受控操作。

## 核心能力

- 客户、工单、会话与消息领域建模
- 工单状态机与业务规则校验
- PostgreSQL 持久化、SQLAlchemy Repository 与 Alembic 迁移
- 基于 OpenAI 兼容接口的大模型客户端
- 原生 Tool Calling、工具注册表和 Agent 多步执行循环
- 会话历史、工具执行轨迹和统一错误处理
- URGENT 工单人工确认等安全约束
- pytest 测试、Ruff 静态检查与格式化

## 技术栈

- Python 3.11+
- FastAPI、Pydantic 2
- SQLAlchemy 2、Alembic、PostgreSQL、Psycopg 3
- OpenAI Python SDK（兼容 OpenAI API 协议的模型服务）
- uv、pytest、Ruff、Docker Compose

## 架构

```text
HTTP API
   │
   ▼
Application Service ── AgentRunner ── LLM Client
   │                         │
   ▼                         ▼
Domain Model           Tool Registry / Tools
   │
   ▼
Repository Interface
   │
   ▼
SQLAlchemy Repository ── PostgreSQL
```

项目通过依赖注入组装请求级数据库 Session、Repository 和 Service。Agent 不直接访问数据库，而是调用受控业务工具，使模型决策与确定性业务逻辑保持分离。

## 本地运行

### 1. 安装依赖

```powershell
uv sync
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写模型 API 配置。`.env` 已被 Git 忽略。

### 3. 启动 PostgreSQL

```powershell
docker compose up -d
uv run alembic upgrade head
```

### 4. 启动服务

```powershell
uv run uvicorn service_desk.main:app --reload
```

启动后访问：

- Swagger UI：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

## 质量检查

```powershell
uv run ruff check .
uv run ruff format . --check
uv run pytest
```

PostgreSQL 集成测试需要先启动并迁移数据库，然后设置 `RUN_POSTGRES_TESTS=1`。

## 当前状态

已完成客户支持核心业务、PostgreSQL 持久化以及真实模型 Tool Calling 的本地端到端流程。后续将继续演进 RAG 知识库、Agent 评测、可观测性和容器化交付能力。
