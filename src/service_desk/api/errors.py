from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from service_desk.agent.exceptions import (
    AgentEmptyResponse,
    AgentMaxStepsExceeded,
)
from service_desk.domain.exceptions import (
    ConversationAlreadyClosed,
    ConversationAlreadyExists,
    ConversationNotFound,
    CustomerAlreadyExists,
    CustomerInactive,
    CustomerNotFound,
    InvalidTicketTransition,
    MessageAlreadyExists,
    TicketAlreadyExists,
    TicketNotFound,
)
from service_desk.llm.exceptions import LLMError
from service_desk.schemas.error import ErrorResponse


async def customer_not_found_handler(
    _request: Request,
    exc: CustomerNotFound,
) -> JSONResponse:
    error = ErrorResponse(
        code="customer_not_found",
        message=f"Customer '{exc.customer_id}' was not found",
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error.model_dump(),
    )


async def customer_already_exists_handler(
    _request: Request, exc: CustomerAlreadyExists
) -> JSONResponse:
    error = ErrorResponse(
        code="customer_already_exists",
        message=f"Customer '{exc.customer_id}' already exists",
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def ticket_not_found_handler(_request: Request, exc: TicketNotFound) -> JSONResponse:
    error = ErrorResponse(code="ticket_not_found", message=f"ticket '{exc.ticket_id}' not found")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error.model_dump(),
    )


async def ticket_already_exists_handler(
    _request: Request, exc: TicketAlreadyExists
) -> JSONResponse:
    error = ErrorResponse(
        code="ticket_already_exists", message=f"ticket '{exc.ticket_id}' already exists"
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def customer_inactive_handler(_request: Request, exc: CustomerInactive) -> JSONResponse:
    error = ErrorResponse(
        code="customer_inactive", message=f"customer '{exc.customer_id}' inactive"
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def invalid_ticket_transition_handler(
    _request: Request,
    exc: InvalidTicketTransition,
) -> JSONResponse:
    error = ErrorResponse(
        code="invalid_ticket_transition",
        message=(
            f"Ticket '{exc.ticket_id}' cannot transition "
            f"from '{exc.current_status}' to '{exc.target_status}'"
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def conversation_not_found_handler(
    _request: Request,
    exc: ConversationNotFound,
) -> JSONResponse:
    error = ErrorResponse(
        code="conversation_not_found",
        message=(f"Conversation '{exc.conversation_id}' was not found"),
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error.model_dump(),
    )


async def conversation_already_exists_handler(
    _request: Request,
    exc: ConversationAlreadyExists,
) -> JSONResponse:
    error = ErrorResponse(
        code="conversation_already_exists",
        message=(f"Conversation '{exc.conversation_id}' already exists"),
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def conversation_already_closed_handler(
    _request: Request,
    exc: ConversationAlreadyClosed,
) -> JSONResponse:
    error = ErrorResponse(
        code="conversation_already_closed",
        message=(f"Conversation '{exc.conversation_id}' is already closed"),
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def message_already_exists_handler(
    _request: Request,
    exc: MessageAlreadyExists,
) -> JSONResponse:
    error = ErrorResponse(
        code="message_already_exists",
        message=f"Message '{exc.message_id}' already exists",
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error.model_dump(),
    )


async def llm_error_handler(
    _request: Request,
    exc: LLMError,
) -> JSONResponse:
    error = ErrorResponse(
        code="llm_service_error",
        message=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error.model_dump(),
    )


async def agent_max_steps_handler(
    _request: Request,
    exc: AgentMaxStepsExceeded,
) -> JSONResponse:
    error = ErrorResponse(
        code="agent_max_steps_exceeded",
        message=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error.model_dump(),
    )


async def agent_empty_response_handler(
    _request: Request,
    exc: AgentEmptyResponse,
) -> JSONResponse:
    error = ErrorResponse(
        code="agent_empty_response",
        message=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=error.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        CustomerNotFound,
        customer_not_found_handler,
    )

    app.add_exception_handler(
        CustomerAlreadyExists,
        customer_already_exists_handler,
    )

    app.add_exception_handler(
        TicketNotFound,
        ticket_not_found_handler,
    )

    app.add_exception_handler(
        TicketAlreadyExists,
        ticket_already_exists_handler,
    )

    app.add_exception_handler(
        CustomerInactive,
        customer_inactive_handler,
    )

    app.add_exception_handler(
        InvalidTicketTransition,
        invalid_ticket_transition_handler,
    )

    app.add_exception_handler(
        ConversationNotFound,
        conversation_not_found_handler,
    )

    app.add_exception_handler(
        ConversationAlreadyExists,
        conversation_already_exists_handler,
    )

    app.add_exception_handler(
        ConversationAlreadyClosed,
        conversation_already_closed_handler,
    )

    app.add_exception_handler(
        MessageAlreadyExists,
        message_already_exists_handler,
    )

    app.add_exception_handler(
        LLMError,
        llm_error_handler,
    )

    app.add_exception_handler(
        AgentMaxStepsExceeded,
        agent_max_steps_handler,
    )

    app.add_exception_handler(
        AgentEmptyResponse,
        agent_empty_response_handler,
    )
