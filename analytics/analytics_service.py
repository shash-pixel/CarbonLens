"""History aggregation helpers for CarbonLens."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from tracking.usage_tracker import TrackedInference


@dataclass(frozen=True)
class HistorySummary:
    """Small, truthful dashboard summary."""

    total_requests: int
    successful_requests: int
    reference_benchmark_count: int
    published_reference_carbon_total_gco2e: float | None
    average_latency_ms: float | None


def history_summary(records: list[TrackedInference]) -> HistorySummary:
    """Calculate metrics without treating missing values as zero."""
    successful_records = [
        record
        for record in records
        if record.status == "success"
    ]

    reference_records = [
        record
        for record in successful_records
        if (
            record.estimation_classification == "reference_benchmark"
            and record.reference_carbon_gco2e is not None
        )
    ]

    latency_values = [
        record.latency_ms
        for record in successful_records
        if record.latency_ms is not None
    ]

    reference_total = None

    if reference_records:
        reference_total = sum(
            record.reference_carbon_gco2e
            for record in reference_records
            if record.reference_carbon_gco2e is not None
        )

    average_latency = None

    if latency_values:
        average_latency = sum(latency_values) / len(latency_values)

    return HistorySummary(
        total_requests=len(records),
        successful_requests=len(successful_records),
        reference_benchmark_count=len(reference_records),
        published_reference_carbon_total_gco2e=reference_total,
        average_latency_ms=average_latency,
    )


def records_to_dataframe(
    records: list[TrackedInference],
) -> pd.DataFrame:
    """Create a safe table for dashboard charts and history display."""
    rows = [
        {
            "timestamp": record.timestamp,
            "provider": record.provider,
            "model": record.model,
            "status": record.status,
            "latency_ms": record.latency_ms,
            "input_tokens": record.input_tokens,
            "output_tokens": record.output_tokens,
            "total_tokens": record.total_tokens,
            "reference_energy_wh": record.reference_energy_wh,
            "reference_carbon_gco2e": record.reference_carbon_gco2e,
            "estimation_method": record.estimation_method,
            "estimation_classification": (
                record.estimation_classification
            ),
            "error_category": record.error_category,
        }
        for record in records
    ]

    return pd.DataFrame(rows)