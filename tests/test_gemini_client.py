from types import SimpleNamespace

import pytest

from integrations.gemini_client import GeminiClient, ProviderError


def test_parse_response_extracts_available_usage_metadata() -> None:
    response = SimpleNamespace(
        text="Hello from Gemini",
        response_id="provider-request-id",
        usage_metadata=SimpleNamespace(
            prompt_token_count=4,
            candidates_token_count=8,
            total_token_count=12,
        ),
    )

    result = GeminiClient._parse_response(
        response=response,
        model="gemini-2.5-flash",
    )

    assert result.provider == "google"
    assert result.response_text == "Hello from Gemini"
    assert result.input_tokens == 4
    assert result.output_tokens == 8
    assert result.total_tokens == 12
    assert result.provider_request_id == "provider-request-id"


def test_parse_response_preserves_missing_usage_metadata() -> None:
    response = SimpleNamespace(
        text="Hello from Gemini",
        response_id=None,
        usage_metadata=None,
    )

    result = GeminiClient._parse_response(
        response=response,
        model="gemini-2.5-flash",
    )

    assert result.input_tokens is None
    assert result.output_tokens is None
    assert result.total_tokens is None


def test_parse_response_rejects_missing_text() -> None:
    response = SimpleNamespace(
        text=None,
        usage_metadata=None,
    )

    with pytest.raises(ProviderError, match="no displayable text"):
        GeminiClient._parse_response(
            response=response,
            model="gemini-2.5-flash",
        )


def test_generate_requires_api_key() -> None:
    client = GeminiClient(api_key=None)

    with pytest.raises(ProviderError) as error:
        client.generate(
            prompt="Hello",
            model="gemini-2.5-flash",
        )

    assert error.value.category == "configuration"