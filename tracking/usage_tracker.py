"""Create normalized records from Gemini request outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE
from integrations.base import ProviderResult


@dataclass(frozen=True)
class TrackedInference:
    """One CarbonLens request outcome.

    response_text is session-only content and must not be persisted by default.
    """

    request_id: str
    timestamp: datetime
    provider: str
    model: str
    status: str
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    provider_request_id: str | None = None
    reference_energy_wh: float | None = None
    reference_carbon_gco2e: float | None = None
    estimation_method: str | None = None
    estimation_classification: str | None = None
    estimation_note: str | None = None
    error_category: str | None = None
    error_message: str | None = None
    response_text: str | None = None


def build_success_record(
    provider_result: ProviderResult,
    latency_ms: float,
) -> TrackedInference:
    """Create a successful tracked request with unscaled published references."""
    reference = GOOGLE_GEMINI_APPS_REFERENCE

    return TrackedInference(
        request_id=str(uuid4()),
        timestamp=datetime.now(UTC),
        provider=provider_result.provider,
        model=provider_result.model,
        status="success",
        latency_ms=latency_ms,
        input_tokens=provider_result.input_tokens,
        output_tokens=provider_result.output_tokens,
        total_tokens=provider_result.total_tokens,
        provider_request_id=provider_result.provider_request_id,
        reference_energy_wh=reference.energy_wh,
        reference_carbon_gco2e=reference.carbon_gco2e,
        estimation_method=reference.method_name,
        estimation_classification="reference_benchmark",
        estimation_note=reference.explanation,
        response_text=provider_result.response_text,
    )


def build_failed_record(
    provider: str,
    model: str,
    error_category: str,
    error_message: str,
) -> TrackedInference:
    """Create a record for a failed request without fabricated reference values."""
    return TrackedInference(
        request_id=str(uuid4()),
        timestamp=datetime.now(UTC),
        provider=provider,
        model=model,
        status="failed",
        error_category=error_category,
        error_message=error_message,
        estimation_method="unavailable",
        estimation_classification="unavailable",
        estimation_note="No environmental reference is stored for a failed request.",
    )