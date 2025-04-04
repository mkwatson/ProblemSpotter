"""Type stubs for OpenAI."""

from typing import Any, Dict, List, Optional

# Module-level variable
api_key: str = ""

class ChatCompletionResponse:
    """Response from a chat completion request."""

    class Choice:
        """A choice in a chat completion response."""

        class Message:
            """A message in a chat completion choice."""

            content: str

        message: Message

    choices: List[Choice]

class ChatCompletion:
    """Chat completion class."""

    @staticmethod
    def create(
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        response_format: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> ChatCompletionResponse:
        """Create a chat completion."""
        ...

class Chat:
    """Chat class."""

    completions: ChatCompletion

# Module-level objects
chat: Chat
