from fastapi import APIRouter, status

from service_desk.api.dependencies import TicketServiceDep
from service_desk.domain.enums import TicketPriority, TicketStatus
from service_desk.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
)

router = APIRouter(prefix="/api/v1/tickets")


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(param: TicketCreate, svc: TicketServiceDep) -> TicketResponse:
    ticket = svc.create_ticket(
        ticket_id=param.id,
        customer_id=param.customer_id,
        title=param.title,
        description=param.description,
        priority=param.priority,
        assignee=param.assignee,
        source=param.source,
    )

    return TicketResponse(
        id=ticket.id,
        customer_id=ticket.customer_id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        assignee=ticket.assignee,
        source=ticket.source,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, svc: TicketServiceDep) -> TicketResponse:
    ticket = svc.get_ticket(ticket_id)

    return TicketResponse(
        id=ticket.id,
        customer_id=ticket.customer_id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        assignee=ticket.assignee,
        source=ticket.source,
    )


@router.get("", response_model=list[TicketResponse])
def get_tickets(
    svc: TicketServiceDep,
    customer_id: str | None = None,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
) -> list[TicketResponse]:
    tickets = svc.list_tickets(customer_id, status, priority)
    result: list[TicketResponse] = []
    for ticket in tickets:
        response = TicketResponse(
            id=ticket.id,
            customer_id=ticket.customer_id,
            title=ticket.title,
            description=ticket.description,
            priority=ticket.priority,
            status=ticket.status,
            assignee=ticket.assignee,
            source=ticket.source,
        )
        result.append(response)

    return result


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_status(
    ticket_id: str,
    param: TicketStatusUpdate,
    svc: TicketServiceDep,
) -> TicketResponse:
    ticket = svc.change_ticket_status(
        ticket_id=ticket_id,
        target_status=param.status,
    )

    return TicketResponse(
        id=ticket.id,
        customer_id=ticket.customer_id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        assignee=ticket.assignee,
        source=ticket.source,
    )
