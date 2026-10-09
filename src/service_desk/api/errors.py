from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from service_desk.domain.exceptions import (
    CustomerAlreadyExists,
    CustomerInactive,
    CustomerNotFound,
    TicketAlreadyExists,
    TicketNotFound,
)
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
