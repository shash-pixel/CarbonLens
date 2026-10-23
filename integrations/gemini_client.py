"""Google Gemini API client for CarbonLens."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from integrations.base import ProviderResult


class ProviderError(Exception):
    """A safe, user-displayable provider error."""

    def __init__(self, category: str, message: str) -> None:
        self.category = category
        super().__init__(message)


class GeminiClient:
    """Small adapter around the official Google GenAI SDK."""

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    def generate(self, prompt: str, model: str) -> tuple[ProviderResult, float]:
        """Send one prompt to Gemini and return parsed metadata plus latency in ms."""
        if not self.api_key:
            raise ProviderError(
                category="configuration",
                message="GEMINI_API_KEY is not configured.",
            )

        try:
            from google import genai
        except ImportError as error:
            raise ProviderError(
                category="configuration",
                message=(
                    "google-genai is not installed. "
                    "Install the project requirements and try again."
                ),
            ) from error

        try:
            client = genai.Client(api_key=self.api_key)

            start = perf_counter()
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            latency_ms = (perf_counter() - start) * 1000

            return self._parse_response(response, model), latency_ms

        except ProviderError:
            raise

        except Exception as error:
            status_code = getattr(error, "code", None)

            if callable(status_code):
                status_code = status_code()

            if status_code is None:
                status_code = getattr(error, "status_code", None)

            diagnostic = error.__class__.__name__

            if status_code is not None:
                diagnostic = f"{diagnostic}, status {str(status_code)[:50]}"

            raise ProviderError(
                category=self._error_category(error),
                message=(
                    f"Gemini request failed ({diagnostic}). "
                    "Check your API key, model access, quota, and connection."
                ),
            ) from error

    @staticmethod
    def _parse_response(response: Any, model: str) -> ProviderResult:
        """Extract only fields CarbonLens needs from a Gemini SDK response."""
        response_text = getattr(response, "text", None)

        if not response_text:
            raise ProviderError(
                category="response",
                message="Gemini returned no displayable text for this request.",
            )

        usage = getattr(response, "usage_metadata", None)

        return ProviderResult(
            provider="google",
            model=model,
            response_text=response_text,
            input_tokens=getattr(usage, "prompt_token_count", None),
            output_tokens=getattr(usage, "candidates_token_count", None),
            total_tokens=getattr(usage, "total_token_count", None),
            provider_request_id=getattr(response, "response_id", None),
        )

    @staticmethod
    def _error_category(error: Exception) -> str:
        """Map changing SDK exception types to stable application categories."""
        error_name = error.__class__.__name__.lower()

        if "auth" in error_name or "permission" in error_name:
            return "authentication"

        if "rate" in error_name or "resourceexhausted" in error_name:
            return "rate_limit"

        if "timeout" in error_name:
            return "timeout"

        return "provider"