"""Bounded OpenAI calls for JSON generation, tutor streaming, and transcription."""

import json
from functools import lru_cache

from config import (
    LLM_MODEL,
    OPENAI_API_KEY,
    OPENAI_MAX_RETRIES,
    OPENAI_TIMEOUT_SECONDS,
    STT_MODEL,
)


class LLMResponseError(ValueError):
    """The provider returned incomplete or structurally invalid JSON."""


@lru_cache(maxsize=1)
def get_client():
    from openai import OpenAI

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=OPENAI_TIMEOUT_SECONDS,
        max_retries=OPENAI_MAX_RETRIES,
    )


def chat_json(messages):
    r = get_client().chat.completions.create(
        model=LLM_MODEL, messages=messages, response_format={"type": "json_object"}
    )
    if not r.choices or not r.choices[0].message.content:
        raise LLMResponseError("The model returned no JSON content.")
    if r.choices[0].finish_reason == "length":
        raise LLMResponseError("The model response was truncated before completion.")
    result = json.loads(r.choices[0].message.content)
    if not isinstance(result, dict):
        raise LLMResponseError("The model must return a JSON object.")
    return result


def chat_stream(messages):
    for chunk in get_client().chat.completions.create(
        model=LLM_MODEL, messages=messages, stream=True
    ):
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def transcribe(audio, filename="answer.webm", context=""):
    kw = {"model": STT_MODEL, "file": (filename, audio)}
    if context:
        kw["prompt"] = context
    return (get_client().audio.transcriptions.create(**kw).text or "").strip()
