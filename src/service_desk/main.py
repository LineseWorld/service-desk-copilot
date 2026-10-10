from contextlib import asynccontextmanager

from fastapi import FastAPI

from service_desk.api.errors import register_exception_handlers
from service_desk.api.routes.conversations import router as conversation_router
from service_desk.api.routes.customers import router as customer_router
from service_desk.api.routes.tickets import router as ticket_router
from service_desk.repositories.memory import (
    InMemoryConversationRepository,
    InMemoryCustomerRepository,
    InMemoryMessageRepository,
    InMemoryTicketRepository,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.customer_repository = InMemoryCustomerRepository()
    app.state.ticket_repository = InMemoryTicketRepository()
    app.state.conversation_repository = InMemoryConversationRepository()
    app.state.message_repository = InMemoryMessageRepository()
    try:
        # yield之后, FastAPI开始接收请求
        yield
    finally:
        # 应用停止时执行一次
        # 当前内存Repository没有需要主动关闭的资源
        pass


def create_app() -> FastAPI:
    app = FastAPI(title="Service Desk Copilot", lifespan=lifespan)

    register_exception_handlers(app)

    app.include_router(customer_router)
    app.include_router(ticket_router)
    app.include_router(conversation_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
