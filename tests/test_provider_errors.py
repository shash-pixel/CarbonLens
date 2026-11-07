import sys
import types

import pytest

from integrations.gemini_client import GeminiClient, ProviderError


class FakeModels:
    def generate_content(self, model: str, contents: str) -> None:
        raise TimeoutError("Simulated network timeout")


class FakeClient:
    def __init__(self, api_key: str) -> None:
        self.models = FakeModels()


def test_generate_converts_timeout_to_safe_provider_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_google_module = types.ModuleType("google")
    fake_google_module.genai = types.SimpleNamespace(
        Client=FakeClient,
    )

    monkeypatch.setitem(
        sys.modules,
        "google",
        fake_google_module,
    )

    client = GeminiClient(api_key="test-key")

    with pytest.raises(ProviderError) as error:
        client.generate(
            prompt="Test prompt",
            model="gemini-3.5-flash-lite",
        )

    assert error.value.category == "timeout"
    assert "Gemini" in str(error.value)
    assert "test-key" not in str(error.value)