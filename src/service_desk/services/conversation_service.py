from datetime import UTC, datetime

from service_desk.domain.enums import ConversationStatus, MessageRole
from service_desk.domain.exceptions import (
    ConversationAlreadyExists,
    ConversationNotFound,
    CustomerNotFound,
    MessageAlreadyExists,
)
from service_desk.domain.models import Conversation, Message
from service_desk.repositories.interfaces import (
    ConversationRepository,
    CustomerRepository,
    MessageRepository,
)


class ConversationService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._customer_repository = customer_repository
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    def create_conversation(
        self,
        *,
        conversation_id: str,
        customer_id: str,
    ) -> Conversation:
        existing_conversation = self._conversation_repository.get_by_id(conversation_id)

        if existing_conversation is not None:
            raise ConversationAlreadyExists(conversation_id)

        customer = self._customer_repository.get_by_id(customer_id)

        if customer is None:
            raise CustomerNotFound(customer_id)

        conversation = Conversation(
            id=conversation_id,
            customer_id=customer_id,
            status=ConversationStatus.OPEN,
            created_at=datetime.now(UTC),
        )

        self._conversation_repository.add(conversation)

        return conversation

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation:
        conversation = self._conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        return conversation

    def add_user_message(
        self,
        *,
        message_id: str,
        conversation_id: str,
        content: str,
    ) -> Message:
        conversation = self._conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        conversation.ensure_accepts_message()

        existing_message = self._message_repository.get_by_id(message_id)

        if existing_message is not None:
            raise MessageAlreadyExists(message_id)

        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
            created_at=datetime.now(UTC),
        )

        self._message_repository.add(message)

        return message

    def list_messages(
        self,
        *,
        conversation_id: str,
        limit: int,
        offset: int,
    ) -> list[Message]:

        conversation = self._conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        return self._message_repository.list_by_conversation(
            conversation_id,
            limit=limit,
            offset=offset,
        )

    def close_conversation(
        self,
        conversation_id: str,
    ) -> Conversation:
        conversation = self._conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        conversation.close()

        self._conversation_repository.update(conversation)

        return conversation
