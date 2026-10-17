from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from service_desk.api.errors import register_exception_handlers
from service_desk.api.routes.agent import router as agent_router
from service_desk.api.routes.conversations import router as conversation_router
from service_desk.api.routes.customers import router as customer_router
from service_desk.api.routes.tickets import router as ticket_router
from service_desk.database.session import engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    try:
        # yield之后, FastAPI开始接收请求
        yield
    finally:
        # 应用停止时执行一次
        engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Service Desk Copilot", lifespan=lifespan)

    register_exception_handlers(app)

    app.include_router(customer_router)
    app.include_router(ticket_router)
    app.include_router(conversation_router)
    app.include_router(agent_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
