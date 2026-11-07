"""History aggregation and filtering helpers for CarbonLens."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from tracking.usage_tracker import TrackedInference

DATAFRAME_COLUMNS = [
    "request_id",
    "timestamp",
    "provider",
    "model",
    "status",
    "latency_ms",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "reference_energy_wh",
    "reference_carbon_gco2e",
    "estimation_method",
    "estimation_classification",
    "error_category",
]


@dataclass(frozen=True)
class HistorySummary:
    """Truthful dashboard summary derived from persisted records."""

    total_requests: int
    successful_requests: int
    token_metadata_count: int
    reference_benchmark_count: int
    published_reference_carbon_total_gco2e: float | None
    average_latency_ms: float | None


def history_summary(records: list[TrackedInference]) -> HistorySummary:
    """Calculate summary metrics without replacing missing data with zero."""
    successful_records = [
        record
        for record in records
        if record.status == "success"
    ]

    token_metadata_records = [
        record
        for record in successful_records
        if (
            record.input_tokens is not None
            or record.output_tokens is not None
            or record.total_tokens is not None
        )
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
        token_metadata_count=len(token_metadata_records),
        reference_benchmark_count=len(reference_records),
        published_reference_carbon_total_gco2e=reference_total,
        average_latency_ms=average_latency,
    )


def records_to_dataframe(
    records: list[TrackedInference],
) -> pd.DataFrame:
    """Create a safe dataframe without raw prompts or responses."""
    rows = [
        {
            "request_id": record.request_id,
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

    return pd.DataFrame(rows, columns=DATAFRAME_COLUMNS)


def filter_history_dataframe(
    dataframe: pd.DataFrame,
    start_date: date | None = None,
    end_date: date | None = None,
    model: str | None = None,
) -> pd.DataFrame:
    """Filter records by inclusive date range and model without database changes."""
    if dataframe.empty:
        return dataframe.copy()

    filtered = dataframe.copy()
    filtered["timestamp"] = pd.to_datetime(
        filtered["timestamp"],
        errors="coerce",
        utc=True,
    )
    filtered = filtered.dropna(subset=["timestamp"])

    if start_date is not None:
        filtered = filtered[
            filtered["timestamp"].dt.date >= start_date
        ]

    if end_date is not None:
        filtered = filtered[
            filtered["timestamp"].dt.date <= end_date
        ]

    if model is not None and model != "All models":
        filtered = filtered[filtered["model"] == model]

    return filtered


def daily_request_activity(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Count actual recorded requests per day."""
    if dataframe.empty:
        return pd.DataFrame(columns=["date", "request_count"])

    chart_data = dataframe.copy()
    chart_data["date"] = pd.to_datetime(
        chart_data["timestamp"],
        errors="coerce",
        utc=True,
    ).dt.date
    chart_data = chart_data.dropna(subset=["date"])

    if chart_data.empty:
        return pd.DataFrame(columns=["date", "request_count"])

    return (
        chart_data.groupby("date", as_index=False)
        .size()
        .rename(columns={"size": "request_count"})
    )


def daily_reference_emissions(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate only published-reference benchmark records by day."""
    if dataframe.empty:
        return pd.DataFrame(
            columns=["date", "reference_carbon_gco2e"]
        )

    reference_records = dataframe[
        (dataframe["status"] == "success")
        & (
            dataframe["estimation_classification"]
            == "reference_benchmark"
        )
        & dataframe["reference_carbon_gco2e"].notna()
    ].copy()

    if reference_records.empty:
        return pd.DataFrame(
            columns=["date", "reference_carbon_gco2e"]
        )

    reference_records["date"] = pd.to_datetime(
        reference_records["timestamp"],
        errors="coerce",
        utc=True,
    ).dt.date
    reference_records = reference_records.dropna(subset=["date"])

    if reference_records.empty:
        return pd.DataFrame(
            columns=["date", "reference_carbon_gco2e"]
        )

    return (
        reference_records.groupby(
            "date",
            as_index=False,
        )["reference_carbon_gco2e"]
        .sum()
    )
