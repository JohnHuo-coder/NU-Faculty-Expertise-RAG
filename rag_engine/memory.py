"""
Conversation memory with summarization to avoid unbounded growth.
Keeps recent turns in full and summarizes older ones when the buffer gets large.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage


SUMMARY_PROMPT = """Summarize the following conversation between the user and the assistant in a concise paragraph. Preserve: key topics, names (e.g. professors, labs), and any follow-up the user said they want. Keep it under 150 words.

Conversation:
{conversation}

Summary:"""


class ConversationMemory:
    """
    In-memory conversation history with automatic summarization.
    When the number of message pairs exceeds `max_messages_before_summary`,
    older turns are summarized via the LLM and only `recent_turns_to_keep` remain in full.
    """

    def __init__(
        self,
        llm,
        max_messages_before_summary: int = 10,
        recent_turns_to_keep: int = 4,
    ):
        self.llm = llm
        self.max_messages_before_summary = max_messages_before_summary
        self.recent_turns_to_keep = recent_turns_to_keep
        self._summary = ""
        self._messages: list[dict] = []  # [{"role": "user"|"assistant", "content": str}, ...]

    def add_turn(self, user_content: str, assistant_content: str) -> None:
        """Append one user/assistant turn and optionally summarize if over limit."""
        self._messages.append({"role": "user", "content": user_content})
        self._messages.append({"role": "assistant", "content": assistant_content})
        self._maybe_summarize()

    def _maybe_summarize(self) -> None:
        # Count full turns (pairs of user + assistant)
        n_turns = len(self._messages) // 2
        if n_turns <= self.max_messages_before_summary:
            return
        # Number of turns to summarize (old ones)
        to_summarize_turns = n_turns - self.recent_turns_to_keep
        if to_summarize_turns <= 0:
            return
        # Messages to summarize: first 2 * to_summarize_turns
        to_summarize = self._messages[: 2 * to_summarize_turns]
        conversation_text = self._format_messages(to_summarize)
        prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)
        chain = prompt | self.llm
        result = chain.invoke({"conversation": conversation_text})
        summary_content = result.content if hasattr(result, "content") else str(result)
        self._summary = summary_content.strip()
        # Keep only recent messages
        self._messages = self._messages[2 * to_summarize_turns :]

    def _format_messages(self, messages: list[dict]) -> str:
        lines = []
        for m in messages:
            role = "User" if m["role"] == "user" else "Assistant"
            lines.append(f"{role}: {m['content']}")
        return "\n\n".join(lines)

    def get_chat_history_for_prompt(self) -> str:
        """
        Returns a string to inject into the RAG prompt (previous conversation).
        Empty string if no history.
        """
        if not self._summary and not self._messages:
            return ""
        parts = []
        if self._summary:
            parts.append(f"Previous conversation (summary):\n{self._summary}\n\n")
        if self._messages:
            parts.append("Recent conversation:\n")
            parts.append(self._format_messages(self._messages))
            parts.append("\n\n")
        return "Previous conversation:\n\n" + "".join(parts)

    def clear(self) -> None:
        """Clear all stored summary and messages."""
        self._summary = ""
        self._messages = []

    @property
    def is_empty(self) -> bool:
        return not self._summary and not self._messages
