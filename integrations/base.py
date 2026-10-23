"""Provider-neutral result models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderResult:
    """Safe metadata returned after a successful provider request."""

    provider: str
    model: str
    response_text: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    provider_request_id: str | None = None