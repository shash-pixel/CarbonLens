"""Published Gemini environmental reference benchmark.

This module intentionally does not estimate energy from token counts or latency.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PublishedReference:
    """A cited environmental benchmark, not request-specific telemetry."""

    energy_wh: float
    carbon_gco2e: float
    method_name: str
    explanation: str
    source_url: str


GOOGLE_GEMINI_APPS_REFERENCE = PublishedReference(
    energy_wh=0.24,
    carbon_gco2e=0.03,
    method_name=(
        "Google published median Gemini Apps text-prompt benchmark "
        "(May 2025 analysis)"
    ),
    explanation=(
        "Published reference values, not direct measurements of this Gemini API "
        "request. The benchmark covers a median Gemini Apps text prompt and a "
        "full serving-system boundary. CarbonLens does not scale these values "
        "by token count or latency."
    ),
    source_url="https://arxiv.org/abs/2508.15734",
)