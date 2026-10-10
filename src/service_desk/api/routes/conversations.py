from fastapi import APIRouter, Query, status

from service_desk.api.dependencies import ConversationServiceDep
from service_desk.domain.models import Conversation, Message
from service_desk.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)
from service_desk.schemas.message import (
    MessageResponse,
    UserMessageCreate,
)

router = APIRouter(prefix="/api/v1/conversations")


def to_conversation_response(conversation: Conversation) -> ConversationResponse:
    return ConversationResponse(
        id=conversation.id,
        customer_id=conversation.customer_id,
        status=conversation.status,
        created_at=conversation.created_at,
    )


def to_message_response(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    param: ConversationCreate,
    svc: ConversationServiceDep,
) -> ConversationResponse:
    conversation = svc.create_conversation(
        conversation_id=param.id,
        customer_id=param.customer_id,
    )

    return to_conversation_response(conversation)


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(conversation_id: str, svc: ConversationServiceDep) -> ConversationResponse:
    conversation = svc.get_conversation(conversation_id)
    return to_conversation_response(conversation)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_user_message(
    conversation_id: str,
    param: UserMessageCreate,
    svc: ConversationServiceDep,
) -> MessageResponse:
    message = svc.add_user_message(
        message_id=param.id,
        conversation_id=conversation_id,
        content=param.content,
    )

    return to_message_response(message)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(
    conversation_id: str,
    svc: ConversationServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[MessageResponse]:
    messages = svc.list_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    return [to_message_response(message) for message in messages]


@router.patch(
    "/{conversation_id}/close",
    response_model=ConversationResponse,
)
def close_conversation(
    conversation_id: str,
    svc: ConversationServiceDep,
) -> ConversationResponse:
    conversation = svc.close_conversation(conversation_id)

    return to_conversation_response(conversation)
