from datetime import UTC, datetime

import pytest

from service_desk.domain.enums import ConversationStatus
from service_desk.domain.exceptions import ConversationAlreadyClosed
from service_desk.domain.models import Conversation


def make_conversation(
    status: ConversationStatus = ConversationStatus.OPEN,
) -> Conversation:
    return Conversation(
        id="conversation-001",
        customer_id="customer-001",
        status=status,
        created_at=datetime.now(UTC),
    )


def test_open_conversation_can_be_closed() -> None:
    conversation = make_conversation()

    conversation.close()

    assert conversation.status == ConversationStatus.CLOSED


def test_closed_conversation_cannot_be_closed_again() -> None:
    conversation = make_conversation(ConversationStatus.CLOSED)

    with pytest.raises(ConversationAlreadyClosed) as exc_info:
        conversation.close()

    assert exc_info.value.conversation_id == conversation.id
    assert conversation.status == ConversationStatus.CLOSED


def test_open_conversation_accepts_messages() -> None:
    conversation = make_conversation()

    conversation.ensure_accepts_message()


def test_closed_conversation_rejects_messages() -> None:
    conversation = make_conversation(ConversationStatus.CLOSED)

    with pytest.raises(ConversationAlreadyClosed) as exc_info:
        conversation.ensure_accepts_message()

    assert exc_info.value.conversation_id == conversation.id
