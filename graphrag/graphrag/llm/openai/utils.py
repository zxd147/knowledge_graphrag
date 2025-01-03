# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Utility functions for the OpenAI API."""

import json
import logging
import re
from collections.abc import Callable
from typing import Any

import tiktoken
from json_repair import repair_json
from openai import (
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)

from .openai_configuration import OpenAIConfiguration

DEFAULT_ENCODING = "cl100k_base"

_encoders: dict[str, tiktoken.Encoding] = {}

RETRYABLE_ERRORS: list[type[Exception]] = [
    RateLimitError,
    APIConnectionError,
    InternalServerError,
]
RATE_LIMIT_ERRORS: list[type[Exception]] = [RateLimitError]

log = logging.getLogger(__name__)


def get_token_counter(config: OpenAIConfiguration) -> Callable[[str], int]:
    """Get a function that counts the number of tokens in a string."""
    model = config.encoding_model or "cl100k_base"
    enc = _encoders.get(model)
    if enc is None:
        enc = tiktoken.get_encoding(model)
        _encoders[model] = enc

    return lambda s: len(enc.encode(s))


def perform_variable_replacements(
    input: str, history: list[dict], variables: dict | None
) -> str:
    """Perform variable replacements on the input string and in a chat log."""
    result = input

    def replace_all(input: str) -> str:
        result = input
        if variables:
            for entry in variables:
                result = result.replace(f"{{{entry}}}", variables[entry])
        return result

    result = replace_all(result)
    for i in range(len(history)):
        entry = history[i]
        if entry.get("role") == "system":
            history[i]["content"] = replace_all(entry.get("content") or "")

    return result


def get_completion_cache_args(configuration: OpenAIConfiguration) -> dict:
    """Get the cache arguments for a completion LLM."""
    return {
        "model": configuration.model,
        "temperature": configuration.temperature,
        "frequency_penalty": configuration.frequency_penalty,
        "presence_penalty": configuration.presence_penalty,
        "top_p": configuration.top_p,
        "max_tokens": configuration.max_tokens,
        "n": configuration.n,
    }


def get_completion_llm_args(
    parameters: dict | None, configuration: OpenAIConfiguration
) -> dict:
    """Get the arguments for a completion LLM."""
    return {
        **get_completion_cache_args(configuration),
        **(parameters or {}),
    }


def try_parse_json_object(input: str) -> tuple[str, dict]:
    """JSON cleaning and formatting utilities."""
    # Sometimes, the LLM returns a json string with some extra description, this function will clean it up.

    result = None
    try:
        # Try parse first
        result = json.loads(input)
        log.info(f"success load json in step 1{result}")
    except json.JSONDecodeError:
        log.warning("Warning: fail to decoding faulty json, attempting repair, attempt to clean up input strings and Markdown frameworks")

    if result:
        return input, result

    _pattern = r"\{(.*)\}"
    _match = re.search(_pattern, input)
    input = "{" + _match.group(1) + "}" if _match else input

    # Clean up json string.
    input = (
        input.replace("{{", "{")
        .replace("}}", "}")
        .replace('"[{', "[{")
        .replace('}]"', "}]")
        .replace("\\", " ")
        .replace("\\n", " ")
        .replace("\n", " ")
        .replace("\r", "")
        .strip()
    )

    # Remove JSON Markdown Frame
    if input.startswith("```json"):
        input = input[len("```json") :]
    if input.endswith("```"):
        input = input[: len(input) - len("```")]

    try:
        result = json.loads(input)
        log.info(f"success load json in step 2{result}")
    except json.JSONDecodeError:
        log.info(f"Warn: JSONDecodeError{input}")

        # Fixup potentially malformed json string using json_repair.
        input = str(repair_json(json_str=input, return_objects=False))

        # Generate JSON-string output using best-attempt prompting & parsing techniques.
        try:
            result = json.loads(input)
        except json.JSONDecodeError:
            log.info(f"===XXX===Execution: JSONDecodeError, error loading json, result=None, json={input}")
            return input, {}
        else:
            if not isinstance(result, dict):
                log.info(f"===XXX===Execution: not expected dict type. result: {result}, result will be None, type=%s:", type(result))
                return input, {}
            log.info(f"success load json in step 3{result}")
            return input, result
    else:
        return input, result


def get_sleep_time_from_error(e: Any) -> float:
    """Extract the sleep time value from a RateLimitError. This is usually only available in Azure."""
    sleep_time = 0.0
    if isinstance(e, RateLimitError) and _please_retry_after in str(e):
        # could be second or seconds
        sleep_time = int(str(e).split(_please_retry_after)[1].split(" second")[0])

    return sleep_time


_please_retry_after = "Please retry after "
