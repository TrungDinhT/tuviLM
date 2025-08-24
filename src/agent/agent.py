from __future__ import annotations

from typing import Annotated, Any, Literal, Sequence, TypedDict, Unpack, cast
import httpx
import annotated_types as at

import openai
from openai.types.chat import ChatCompletionMessageParam


Role = Literal["system", "assistant", "user", "developer"]


class LLMMessage(TypedDict):
    """Lighter version of OpenAI API."""

    role: Role
    content: str

class LLMParameters(TypedDict, total=False):
    """Subset of OpenAI model parameters."""

    temperature: Annotated[float, at.Ge(0.0)]
    max_tokens: Annotated[int, at.Ge(1)]
    stop: Annotated[list[Annotated[str, at.MinLen(1)]], at.MinLen(1)]
    seed: Annotated[int, at.Ge(0)]

class ChatAgent:
    """
    Agent uses OpenAI Responses API.
    """
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        messages: Sequence[LLMMessage] = (),
        timeout: httpx.Timeout = httpx.Timeout(connect=5.0, timeout=30.0),
        **kwargs: Unpack[LLMParameters],
    ):
        self.messages = tuple(messages)
        self.model = model
        self.parameters = kwargs.copy()

        self._client = openai.Client(timeout=timeout)


    def run(
        self,
        input_: Sequence[LLMMessage],
        **params: Any,
    ) -> str:

        messages = [*self.messages, *input_]

        try:
            response = self._client.chat.completions.create(
                # NOTE : We're more restrictive than the OpenAI models
                messages=cast(list[ChatCompletionMessageParam], messages),
                model=self.model,
                **{**self.parameters, **params},
            )
        except openai.OpenAIError as e:
            # Re-raise OpenAI specific errors
            raise e
        except Exception as e:
            # Re-raise any other unexpected errors
            raise e

        return response.choices[0].message.content or ""
