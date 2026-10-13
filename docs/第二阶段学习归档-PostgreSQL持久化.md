# 第二阶段学习归档：Docker、PostgreSQL、SQLAlchemy 与 Alembic

> 项目：Service Desk Copilot
>
> 阶段目标：把原来的内存 Repository 替换为 PostgreSQL 持久化实现，同时保留分层结构和快速测试能力。
>
> 当前技术栈：Python 3.11、FastAPI、PostgreSQL 17、SQLAlchemy 2.1、Psycopg 3、Alembic、Docker Compose、uv。

## 1. 本阶段完成了什么

本阶段将原来的调用链：

```text
Router
  -> Service
  -> Repository 接口
  -> InMemory Repository
  -> Python dict
```

扩展为正式运行时的数据库链路：

```text
HTTP 请求
  -> FastAPI Router
  -> Service
  -> Repository 接口
  -> SQLAlchemy Repository
  -> SQLAlchemy Session
  -> Engine / 连接池
  -> Psycopg
  -> PostgreSQL
```

测试仍然可以通过 FastAPI 的 `dependency_overrides` 使用内存 Repository：

```text
API 测试
  -> dependency_overrides
  -> InMemory Repository
```

这样既保留了快速测试，也让正式服务具备数据持久化能力。

当前主要文件：

| 文件 | 职责 |
|---|---|
| `compose.yaml` | 定义本地 PostgreSQL 容器 |
| `.env.example` | 环境变量示例，不保存真实生产密码 |
| `src/service_desk/config.py` | 使用 Pydantic Settings 读取配置 |
| `src/service_desk/database/base.py` | SQLAlchemy ORM 公共基类 |
| `src/service_desk/database/models.py` | ORM Model 和数据库表结构 |
| `src/service_desk/database/session.py` | Engine、SessionFactory、请求级 Session |
| `src/service_desk/repositories/sqlalchemy.py` | SQLAlchemy Repository 实现和对象转换 |
| `src/service_desk/api/dependencies.py` | Session、Repository、Service 的依赖组装 |
| `alembic.ini` | Alembic 入口配置 |
| `alembic/env.py` | Alembic 运行环境、数据库地址和 Metadata |
| `alembic/versions/` | 数据库迁移历史 |

---

## 2. 每个技术组件解决什么问题

| 组件 | 解决的问题 |
|---|---|
| Docker Desktop | 在 Windows 上提供 Docker Engine 和管理界面 |
| Docker Compose | 使用一个 YAML 文件启动和管理 PostgreSQL 服务 |
| PostgreSQL | 真正保存客户、工单、会话和消息数据 |
| Psycopg | Python 与 PostgreSQL 通信的底层驱动 |
| SQLAlchemy Engine | 管理数据库方言、驱动和连接池 |
| SQLAlchemy Session | 管理一次业务操作中的查询、对象变化和事务 |
| SQLAlchemy ORM | 将 Python ORM 类映射到数据库表 |
| Alembic | 记录并执行数据库表结构的版本变化 |
| Pydantic Settings | 从系统环境变量或 `.env` 读取配置 |
| FastAPI Depends | 按请求创建 Session、Repository 和 Service |
| uv | 管理依赖、虚拟环境、锁文件和命令执行 |

需要特别区分：

```text
Docker 负责运行 PostgreSQL
PostgreSQL 负责保存数据
SQLAlchemy 负责让 Python 操作数据库
Alembic 负责改变数据库结构
FastAPI 负责 HTTP 请求和依赖生命周期
```

---

## 3. Windows 安装 Docker

### 3.1 安装前检查

当前电脑是 x64 AMD 处理器，应安装 Windows AMD64/x86_64 版本的 Docker Desktop。

先检查虚拟化：

1. 打开任务管理器；
2. 进入“性能 -> CPU”；
3. 确认“虚拟化”显示为“已启用”。

检查 WSL：

```powershell
wsl --version
```

如果尚未安装：

```powershell
wsl --install
```

执行后通常需要重启 Windows。

### 3.2 安装和验证 Docker Desktop

安装 Docker Desktop 后启动它，等待界面显示 Docker Engine 正常运行，再执行：

```powershell
docker --version
docker compose version
docker version
```

`docker version` 应同时显示：

```text
Client
Server
```

如果只有 Client，没有 Server，说明 Docker CLI 已安装，但 Docker Engine 尚未启动。

### 3.3 VS Code 识别不到 Docker

如果普通 CMD 能运行 `docker`，但 VS Code PowerShell 提示找不到命令，通常是 VS Code 仍持有安装前的旧 `PATH`。

处理方法：

1. 完全关闭所有 VS Code 窗口；
2. 重新打开 VS Code；
3. 新建终端；
4. 执行：

```powershell
where.exe docker
docker --version
```

### 3.4 Docker Engine 未运行

如果出现：

```text
failed to connect to the docker API
npipe:////./pipe/docker_engine
```

含义是 Docker CLI 存在，但后台 Docker Engine 没有运行。启动 Docker Desktop并等待 Engine正常后重试。

官方资料：

- [Docker Desktop for Windows 安装](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker Desktop WSL 2 后端](https://docs.docker.com/desktop/features/wsl/)
- [Microsoft WSL 安装](https://learn.microsoft.com/windows/wsl/install)

---

## 4. Docker Compose 与当前 PostgreSQL

当前 `compose.yaml` 的核心结构：

```yaml
services:
  postgres:
    image: postgres:17
    container_name: service-desk-postgres
    environment:
      POSTGRES_DB: service_desk
      POSTGRES_USER: service_desk
      POSTGRES_PASSWORD: service_desk
    ports:
      - "5432:5432"
    volumes:
      - service_desk_postgres_data:/var/lib/postgresql/data
```

字段含义：

| 配置 | 含义 |
|---|---|
| `image: postgres:17` | 使用 PostgreSQL 17 官方镜像 |
| `container_name` | 指定本地容器名称 |
| `POSTGRES_DB` | 首次初始化时创建的数据库 |
| `POSTGRES_USER` | 首次初始化时创建的数据库用户 |
| `POSTGRES_PASSWORD` | 该用户的密码 |
| `5432:5432` | Windows 5432 映射到容器 5432 |
| `volumes` | 把数据库文件保存在 Docker Volume 中 |

对于 PostgreSQL 17，数据卷挂载到 `/var/lib/postgresql/data` 是正确的。初始化环境变量只在空数据目录首次启动时生效；已有 Volume 时，修改它们不会自动重建数据库。[PostgreSQL Docker Official Image](https://hub.docker.com/_/postgres)

### 4.1 常用 Compose 命令

检查 YAML：

```powershell
docker compose config
```

后台启动：

```powershell
docker compose up -d
```

查看服务状态：

```powershell
docker compose ps
```

查看 PostgreSQL 日志：

```powershell
docker compose logs postgres
docker compose logs -f postgres
```

停止但不删除容器：

```powershell
docker compose stop
```

重新启动：

```powershell
docker compose start
docker compose restart postgres
```

删除容器和网络但保留数据卷：

```powershell
docker compose down
```

删除容器并删除数据卷：

```powershell
docker compose down -v
```

`down -v` 会删除数据库数据，只能在明确不需要数据时执行。

官方资料：[Docker Compose 文档](https://docs.docker.com/compose/)

---

## 5. PostgreSQL 基础概念与操作

层级关系：

```text
PostgreSQL Server
  -> Database: service_desk
     -> Schema: public
        -> Table: customers / tickets / conversations / messages
           -> Row
              -> Column
```

### 5.1 进入 psql

项目不要求Windows单独安装 PostgreSQL客户端，可以直接使用容器中的 `psql`：

```powershell
docker exec -it service-desk-postgres `
  psql -U service_desk -d service_desk
```

其中：

| 参数 | 含义 |
|---|---|
| `-U` | 数据库用户名 |
| `-d` | 数据库名称 |
| `-h` | 数据库主机，容器内本地连接时可省略 |
| `-p` | 端口，默认 5432 时可省略 |

### 5.2 psql 常用元命令

```text
\l                 列出数据库
\c service_desk    切换数据库
\dt                列出表
\d customers       查看表结构
\di                查看索引
\dT+               查看数据类型，包括ENUM
\q                 退出psql
```

这些以反斜杠开头的是 `psql` 客户端命令，不是 SQL。

### 5.3 常用 SQL

查询：

```sql
SELECT * FROM customers;

SELECT id, title, status
FROM tickets
WHERE customer_id = 'customer-001'
ORDER BY id;
```

统计：

```sql
SELECT COUNT(*) FROM messages;
```

查看消息索引：

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'messages';
```

理解事务：

```sql
BEGIN;

UPDATE tickets
SET status = 'IN_PROGRESS'
WHERE id = 'ticket-001';

ROLLBACK;
```

如果将 `ROLLBACK` 改成 `COMMIT`，变更才正式提交。

官方资料：

- [PostgreSQL SQL 命令参考](https://www.postgresql.org/docs/current/sql-commands.html)
- [PostgreSQL psql](https://www.postgresql.org/docs/current/app-psql.html)

---

## 6. 数据库连接字符串

当前连接地址：

```text
postgresql+psycopg://service_desk:service_desk@localhost:5432/service_desk
```

拆分理解：

```text
postgresql          SQLAlchemy数据库方言
psycopg             Python数据库驱动
service_desk        用户名
service_desk        密码
localhost           主机
5432                端口
service_desk        数据库名
```

`.env` 中写：

```dotenv
DATABASE_URL=postgresql+psycopg://service_desk:service_desk@localhost:5432/service_desk
```

`Settings` 字段：

```python
database_url: str
```

Pydantic Settings 会把环境变量 `DATABASE_URL` 映射到 Python 字段 `database_url`。

配置来源常见优先级：

```text
Settings构造参数
  > 系统环境变量
  > .env
  > 代码默认值
```

`.env` 可能含真实密码，不提交Git；提交 `.env.example` 说明需要哪些变量。

---

## 7. SQLAlchemy ORM Model

### 7.1 ORM是什么

ORM把数据库表映射成Python类：

```text
customers表       <-> CustomerRecord类
表中的一行         <-> CustomerRecord对象
id/name字段        <-> record.id / record.name属性
```

示例：

```python
class CustomerRecord(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )
```

`Mapped[str]` 表示这个ORM属性在Python中是字符串；`mapped_column()` 描述对应数据库列。

### 7.2 ORM Model与Domain Model为什么分开

```text
CustomerRecord：数据库表映射，属于基础设施层
Customer：业务实体，属于领域层
CustomerResponse：HTTP响应结构，属于API层
```

分开后，领域逻辑不会直接依赖SQLAlchemy。Repository负责转换：

```python
def customer_to_domain(record: CustomerRecord) -> Customer: ...


def customer_to_record(customer: Customer) -> CustomerRecord: ...
```

### 7.3 主键、外键、唯一约束和索引

- 主键：唯一识别一行，例如 `customers.id`；
- 外键：保证引用目标存在，例如 `tickets.customer_id -> customers.id`；
- 唯一约束：保证某列或某组列不能重复；
- 索引：提高特定查询速度，但会增加写入和存储成本。

消息索引：

```python
Index(
    "ix_messages_conversation_created_at_id",
    "conversation_id",
    "created_at",
    "id",
)
```

服务于：

```sql
SELECT *
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at, id;
```

`id` 是相同时间戳下的稳定排序字段。

---

## 8. Engine、SessionFactory与Session

### 8.1 Engine

```python
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)
```

Engine是应用级对象，主要管理：

- 数据库方言；
- Psycopg驱动；
- 数据库地址；
- 连接池。

创建Engine通常不会马上连接数据库，而是在第一次真正执行数据库操作时懒连接。[SQLAlchemy Engine官方文档](https://docs.sqlalchemy.org/en/21/tutorial/engine.html)

### 8.2 SessionFactory

```python
SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)
```

它是Session工厂，不是Session本身：

```python
session_a = SessionFactory()
session_b = SessionFactory()

assert session_a is not session_b
```

### 8.3 Session

Session可以理解为一次业务操作的：

```text
数据库工作区 + ORM对象管理器 + 事务边界
```

它维护Identity Map：同一个Session中，相同ORM类型和主键通常对应同一个Python对象。

Session不是线程安全的：

```text
Engine可以应用级共享
SessionFactory可以应用级共享
具体Session必须限制在单个请求/任务中
```

官方资料：[SQLAlchemy Session](https://docs.sqlalchemy.org/en/21/orm/session.html)

### 8.4 `autoflush=False`

关闭查询前的自动flush。代码需要明确理解何时把待处理变化发送给数据库。

即使关闭autoflush：

```python
session.commit()
```

仍会在提交前执行必要的flush。

### 8.5 `expire_on_commit=False`

提交后不主动把ORM属性标记为过期，因此读取：

```python
record.name
```

通常直接使用当前内存值，不会因为提交而自动重新查询数据库。它不保证内存值永远是数据库最新值；需要最新值时使用：

```python
session.refresh(record)
```

---

## 9. SQLAlchemy CRUD与SQL关系

### 9.1 根据主键查询

```python
record = session.get(CustomerRecord, customer_id)
```

近似SQL：

```sql
SELECT * FROM customers WHERE id = :customer_id;
```

`get()`会先检查当前Session的Identity Map，没有时才查询数据库。

### 9.2 新增

```python
record = CustomerRecord(...)
session.add(record)
```

`add()`只是把对象交给Session管理，通常不会立即INSERT。

```text
add     -> 标记为待新增
flush   -> 发送INSERT，但事务还未提交
commit  -> flush后正式提交事务
rollback-> 撤销当前事务
```

### 9.3 条件查询与列表

```python
statement = (
    select(MessageRecord)
    .where(MessageRecord.conversation_id == conversation_id)
    .order_by(MessageRecord.created_at, MessageRecord.id)
    .offset(offset)
    .limit(limit)
)

records = session.scalars(statement).all()
```

### 9.4 更新

```python
record = session.get(TicketRecord, ticket.id)
record.status = ticket.status
```

SQLAlchemy会跟踪属性变化，在flush或commit时生成UPDATE。

### 9.5 删除

```python
record = session.get(CustomerRecord, customer_id)
session.delete(record)
```

`delete()`接收ORM对象，不直接接收主键。真正的DELETE在flush或commit时发送。

官方资料：

- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/21/orm/quickstart.html)
- [SQLAlchemy统一教程](https://docs.sqlalchemy.org/en/21/tutorial/)
- [事务与连接管理](https://docs.sqlalchemy.org/en/21/orm/session_transaction.html)

---

## 10. Repository的职责

Repository位于Service与数据库之间：

```text
Service
  -> Repository接口
  -> SQLAlchemy Repository
  -> Session
  -> PostgreSQL
```

它负责：

1. 构造SQLAlchemy查询；
2. ORM Record与Domain Model互相转换；
3. 隐藏数据库技术细节；
4. 返回领域对象，而不是把ORM对象泄露给Service。

Repository通常不调用 `commit()`：

```python
def add(self, customer: Customer) -> None:
    self._session.add(customer_to_record(customer))
```

事务由外层统一提交，保证一次业务操作中的多个Repository操作共同成功或共同回滚。

---

## 11. FastAPI请求级Session与依赖注入

数据库依赖：

```python
def get_db_session() -> Iterator[Session]:
    with SessionFactory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

推荐把数据库依赖设置为函数作用域，让commit发生在HTTP响应发送之前：

```python
DbSessionDep = Annotated[
    Session,
    Depends(get_db_session, scope="function"),
]
```

一次创建工单请求：

```text
FastAPI收到请求
  -> 调用get_db_session()
  -> SessionFactory创建Session A
  -> yield Session A
  -> 创建CustomerRepository(Session A)
  -> 创建TicketRepository(Session A)
  -> 创建TicketService
  -> 执行业务
  -> 路由返回
  -> 恢复get_db_session()
  -> commit或rollback
  -> 关闭Session A
```

同一个请求中，相同依赖默认只执行一次，因此多个Repository共享同一个Session和事务：

```text
请求A：CustomerRepo A、TicketRepo A -> Session A
请求B：CustomerRepo B、TicketRepo B -> Session B
```

官方资料：

- [FastAPI子依赖与请求内缓存](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/)
- [FastAPI带yield的依赖](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)

---

## 12. Alembic原理与命令

Alembic管理的是数据库Schema版本，不是业务数据版本。

可以类比Git：

| Git | Alembic |
|---|---|
| commit | revision |
| commit hash | revision ID |
| git log | alembic history |
| 当前提交 | alembic current |
| 最新提交 | alembic heads |

### 12.1 初始化

一个项目通常只执行一次：

```powershell
uv run alembic init alembic
```

它只生成Alembic目录和配置，不会创建业务表。

### 12.2 自动生成迁移

```powershell
uv run alembic revision --autogenerate -m "创建初始业务表"
```

Alembic比较：

```text
Base.metadata中的期望结构
          ↕
PostgreSQL中的实际结构
```

然后生成候选迁移。自动生成结果必须人工检查，尤其关注：

- 表和字段是否遗漏；
- 外键、索引、唯一约束；
- 字段重命名是否被误判成删除加新增；
- PostgreSQL ENUM是否能正确回退。

### 12.3 执行迁移

```powershell
uv run alembic upgrade head
```

数据库中的 `alembic_version` 表记录当前Revision ID。

### 12.4 常用命令

```powershell
uv run alembic current
uv run alembic heads
uv run alembic history
uv run alembic check
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic downgrade base
```

`downgrade`可能删除表、字段和数据，不能在含重要数据的数据库随意执行。

### 12.5 为什么env.py必须导入models

```python
from service_desk.database import models  # noqa: F401
```

虽然没有直接访问 `models` 变量，但导入过程会执行ORM类定义，把表注册到 `Base.metadata`。

如果删除它，Alembic可能认为Metadata是空的，并生成删除所有业务表的候选操作。

### 12.6 不要随意修改已共享的迁移

Alembic只在 `alembic_version` 中记录Revision ID，不记录迁移文件校验值。

```text
尚未共享、数据库可丢弃
  -> 可以修正初始迁移并重建数据库

迁移已提交、被他人执行或部署
  -> 不修改历史迁移，新增revision
```

官方资料：

- [Alembic官方教程](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic自动生成迁移](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

---

## 13. 当前项目常用命令速查

### 13.1 环境和依赖

```powershell
uv sync --locked
uv run python --version
```

### 13.2 数据库

```powershell
docker compose config
docker compose up -d
docker compose ps
docker compose logs postgres
```

### 13.3 迁移

```powershell
uv run alembic current
uv run alembic heads
uv run alembic check
uv run alembic upgrade head
```

### 13.4 代码质量和测试

```powershell
uv run ruff check .
uv run ruff format . --check
uv run pytest
uv build
```

自动修复普通Ruff问题：

```powershell
uv run ruff check . --fix
uv run ruff format .
```

自动修复后要查看差异，不能不检查就提交：

```powershell
git diff
```

### 13.5 启动服务

```powershell
uv run uvicorn service_desk.main:app --reload
```

访问：

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

---

## 14. 常见故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `docker`无法识别 | PATH未刷新或未安装 | 重启VS Code，执行`where.exe docker` |
| 无法连接`docker_engine` | Docker Desktop/Engine未启动 | 启动Docker Desktop，检查`docker version`的Server |
| `connection refused localhost:5432` | PostgreSQL未启动或端口错误 | `docker compose ps`、查看日志和端口映射 |
| `ModuleNotFoundError: service_desk` | 包未安装或不在项目环境 | `uv sync`，通过`uv run`执行 |
| Alembic检测要删除所有表 | `models.py`未导入，Metadata为空 | 恢复副作用导入并加`# noqa: F401` |
| 修改迁移后`upgrade head`无动作 | 数据库已记录相同Revision ID | 可丢弃环境重建；已共享环境新增迁移 |
| 第二次upgrade提示ENUM已存在 | downgrade没有删除PostgreSQL枚举 | 在迁移downgrade中显式drop ENUM |
| ORM新增后查询不到 | `autoflush=False`且尚未flush | 必要时显式`session.flush()` |
| 提交后访问ORM属性又发SELECT | 默认expire_on_commit行为 | 理解对象过期；当前项目使用`False` |
| pytest仍访问真实数据库 | 依赖覆盖不完整 | 覆盖所有Repository provider并共享内存实例 |

---

## 15. 当前阶段验收标准

基础验收：

```powershell
uv run python -c "from service_desk.main import app; print('app import ok')"
uv run ruff check .
uv run ruff format . --check
uv run pytest
uv build
uv run alembic current
uv run alembic heads
uv run alembic check
```

预期：

```text
应用导入成功
Ruff检查通过
格式检查通过
全部测试通过
构建成功
current等于heads
No new upgrade operations detected
```

数据库持久化验收：

```text
启动服务
  -> 创建客户
  -> 创建工单
  -> 创建会话和消息
  -> 停止并重启FastAPI
  -> 重新查询数据
  -> 数据仍然存在
```

迁移往返验收必须在可丢弃数据库中执行：

```powershell
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic check
```

正式声明本阶段完成前，建议再补充真实PostgreSQL集成测试。当前API测试通过内存Repository运行，只能证明API和业务逻辑正确，不能单独证明SQLAlchemy Repository的增删改查全部正确。

当前项目的PostgreSQL集成测试默认跳过，避免普通快速测试强制依赖Docker。PowerShell中显式运行：

```powershell
$env:RUN_POSTGRES_TESTS = "1"
uv run pytest tests/integration -v
Remove-Item Env:RUN_POSTGRES_TESTS
```

该测试在一个外层事务中执行真实HTTP请求和真实Repository操作。每个请求仍然创建Session并提交Savepoint，测试结束后回滚外层事务，因此不会把测试客户、工单、会话和消息留在开发数据库。

---

## 16. 本阶段需要真正掌握的内容

1. Docker镜像、容器、端口映射、Volume和Compose的区别；
2. PostgreSQL数据库、Schema、表、行、主键、外键、索引和事务；
3. SQLAlchemy Engine、连接池、SessionFactory和Session的职责；
4. `add`、`get`、`select`、`delete`、`flush`、`commit`和`rollback`的执行时机；
5. ORM Model、Domain Model和API Schema为什么需要分层；
6. Repository为什么返回Domain Model，并且通常不自行commit；
7. 一次HTTP请求为什么只创建一个Session；
8. 多个Repository为什么要共享同一个请求事务；
9. Alembic如何比较Metadata和真实数据库结构；
10. 为什么自动生成迁移以后仍然需要人工审查；
11. 为什么内存API测试不能代替PostgreSQL集成测试；
12. 为什么已共享的迁移不能随意修改。

---

## 17. 常见面试问题与回答

### 为什么不用全局Session？

Session是有状态的事务和ORM对象管理器，不是线程安全的。全局共享会让不同请求的事务、对象状态、commit和rollback互相干扰。Engine和SessionFactory可以应用级共享，Session应按请求创建。

### `flush`和`commit`有什么区别？

`flush`把待处理的INSERT、UPDATE和DELETE发送给数据库，但事务仍可回滚；`commit`会先flush，再正式提交事务。

### 为什么Repository不直接commit？

一次业务操作可能调用多个Repository。由外层统一提交，可以保证它们处于同一个事务中，任何一步失败时整体rollback。

### 为什么保留InMemory Repository？

它让Service和普通API测试不依赖Docker和数据库，执行更快。SQLAlchemy实现再通过独立集成测试验证。

### Alembic autogenerate是否完全可靠？

不是。它能比较常见表、字段、约束和索引，但重命名可能被识别为删除加新增，数据库专用类型和数据迁移也可能需要人工代码，因此生成后必须审查。

### ORM是否意味着不需要懂SQL？

不是。ORM最终仍生成SQL。开发者必须理解查询条件、JOIN、索引、事务、约束和执行次数，才能判断正确性和性能。
