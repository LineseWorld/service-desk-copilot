import pytest

from service_desk.domain.enums import TicketPriority, TicketSource, TicketStatus
from service_desk.domain.exceptions import InvalidTicketTransition
from service_desk.domain.models import Ticket


def make_ticket(status: TicketStatus) -> Ticket:
    return Ticket(
        id="ticket-001",
        customer_id="customer-001",
        title="会议无法正常加入",
        description="用户加入会议时出现错误",
        priority=TicketPriority.HIGH,
        status=status,
        assignee=None,
        source=TicketSource.MANUAL,
    )


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        (TicketStatus.OPEN, TicketStatus.IN_PROGRESS),
        (TicketStatus.IN_PROGRESS, TicketStatus.WAITING),
        (TicketStatus.WAITING, TicketStatus.IN_PROGRESS),
        (TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED),
        (TicketStatus.RESOLVED, TicketStatus.CLOSED),
        (TicketStatus.RESOLVED, TicketStatus.IN_PROGRESS),
    ],
)
def test_ticket_allows_valid_transition(
    current_status: TicketStatus,
    target_status: TicketStatus,
) -> None:
    ticket = make_ticket(current_status)

    ticket.transition_to(target_status)

    assert ticket.status == target_status


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        (TicketStatus.OPEN, TicketStatus.OPEN),
        (TicketStatus.OPEN, TicketStatus.RESOLVED),
        (TicketStatus.OPEN, TicketStatus.CLOSED),
        (TicketStatus.WAITING, TicketStatus.CLOSED),
        (TicketStatus.CLOSED, TicketStatus.IN_PROGRESS),
    ],
)
def test_ticket_rejects_invalid_transition(
    current_status: TicketStatus,
    target_status: TicketStatus,
) -> None:
    ticket = make_ticket(current_status)

    with pytest.raises(InvalidTicketTransition) as exc_info:
        ticket.transition_to(target_status)

    assert exc_info.value.ticket_id == ticket.id
    assert exc_info.value.current_status == current_status
    assert exc_info.value.target_status == target_status
    assert ticket.status == current_status
