from datetime import datetime

from pydantic import BaseModel, Field

from service_desk.domain.enums import ConversationStatus


class ConversationCreate(BaseModel):
    id: str = Field(min_length=1, max_length=50)
    customer_id: str = Field(min_length=1, max_length=50)


class ConversationResponse(BaseModel):
    id: str
    customer_id: str
    status: ConversationStatus
    created_at: datetime
