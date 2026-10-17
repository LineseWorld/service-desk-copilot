from uuid import uuid4

from service_desk.agent.models import AgentRunResult
from service_desk.agent.runner import AgentRunner
from service_desk.domain.enums import MessageRole
from service_desk.domain.models import Message
from service_desk.llm.models import ChatMessage
from service_desk.services.conversation_service import ConversationService


class AgentService:
    HISTORY_LIMIT = 50

    def __init__(
        self,
        *,
        runner: AgentRunner,
        conversation_service: ConversationService,
    ) -> None:
        self._runner = runner
        self._conversation_service = conversation_service

    @staticmethod
    def _to_chat_history(messages: list[Message]) -> list[ChatMessage]:
        history: list[ChatMessage] = []

        for message in messages:
            if message.role == MessageRole.USER:
                history.append(ChatMessage.user(message.content))
            elif message.role == MessageRole.ASSISTANT:
                history.append(ChatMessage.assistant(message.content))
        return history

    def run(
        self,
        *,
        conversation_id: str,
        user_message: str,
    ) -> AgentRunResult:
        self._conversation_service.get_conversation(conversation_id)

        sorted_messages = self._conversation_service.list_recent_messages(
            conversation_id=conversation_id,
            limit=self.HISTORY_LIMIT,
        )

        history = self._to_chat_history(sorted_messages)

        self._conversation_service.add_user_message(
            message_id=str(uuid4()),
            conversation_id=conversation_id,
            content=user_message,
        )

        result = self._runner.run(
            user_message=user_message,
            history=history,
        )

        self._conversation_service.add_assistant_message(
            message_id=str(uuid4()),
            conversation_id=conversation_id,
            content=result.answer,
        )

        return result
