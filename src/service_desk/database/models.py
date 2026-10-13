from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from service_desk.database.base import Base
from service_desk.domain.enums import (
    ConversationStatus,
    CustomerPlan,
    CustomerStatus,
    MessageRole,
    TicketPriority,
    TicketSource,
    TicketStatus,
)


class CustomerRecord(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    plan: Mapped[CustomerPlan] = mapped_column(
        SqlEnum(CustomerPlan, name="customer_plan"),
        nullable=False,
    )

    status: Mapped[CustomerStatus] = mapped_column(
        SqlEnum(CustomerStatus, name="customer_status"),
        nullable=False,
    )

    products: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )


class TicketRecord(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SqlEnum(TicketPriority, name="ticket_priority"),
        nullable=False,
    )
    status: Mapped[TicketStatus] = mapped_column(
        SqlEnum(TicketStatus, name="ticket_status"),
        nullable=False,
    )
    assignee: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    source: Mapped[TicketSource] = mapped_column(
        SqlEnum(TicketSource, name="ticket_source"),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_tickets_customer_status",
            "customer_id",
            "status",
        ),
        Index(
            "ix_tickets_priority",
            "priority",
        ),
    )


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SqlEnum(
            ConversationStatus,
            name="conversation_status",
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_conversations_customer_created_at",
            "customer_id",
            "created_at",
        ),
    )


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
    )
    role: Mapped[MessageRole] = mapped_column(
        SqlEnum(MessageRole, name="message_role"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_messages_conversation_created_at_id",
            "conversation_id",
            "created_at",
            "id",
        ),
    )
