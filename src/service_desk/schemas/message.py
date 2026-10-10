from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from service_desk.domain.enums import MessageRole

NonEmptyText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=4000,
    ),
]


class UserMessageCreate(BaseModel):
    id: str = Field(min_length=1, max_length=50)
    content: NonEmptyText


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    created_at: datetime
