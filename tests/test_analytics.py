from datetime import UTC, date, datetime

from analytics.analytics_service import (
    daily_reference_emissions,
    daily_request_activity,
    filter_history_dataframe,
    history_summary,
    records_to_dataframe,
)
from tracking.usage_tracker import TrackedInference


def make_record(
    request_id: str,
    timestamp: datetime,
    status: str = "success",
    model: str = "gemini-3.5-flash-lite",
    latency_ms: float | None = 100,
    total_tokens: int | None = 12,
    reference_carbon_gco2e: float | None = 0.03,
    estimation_classification: str | None = "reference_benchmark",
) -> TrackedInference:
    return TrackedInference(
        request_id=request_id,
        timestamp=timestamp,
        provider="google",
        model=model,
        status=status,
        latency_ms=latency_ms,
        total_tokens=total_tokens,
        reference_carbon_gco2e=reference_carbon_gco2e,
        estimation_classification=estimation_classification,
    )


def test_history_summary_counts_only_available_metadata() -> None:
    records = [
        make_record(
            "request-1",
            datetime(2026, 10, 20, tzinfo=UTC),
        ),
        make_record(
            "request-2",
            datetime(2026, 10, 20, tzinfo=UTC),
            total_tokens=None,
            reference_carbon_gco2e=None,
            estimation_classification="unavailable",
        ),
        make_record(
            "request-3",
            datetime(2026, 10, 20, tzinfo=UTC),
            status="failed",
            latency_ms=None,
            total_tokens=None,
            reference_carbon_gco2e=None,
            estimation_classification="unavailable",
        ),
    ]

    summary = history_summary(records)

    assert summary.total_requests == 3
    assert summary.successful_requests == 2
    assert summary.token_metadata_count == 1
    assert summary.reference_benchmark_count == 1
    assert summary.published_reference_carbon_total_gco2e == 0.03
    assert summary.average_latency_ms == 100


def test_history_filter_supports_dates_and_models() -> None:
    records = [
        make_record(
            "request-1",
            datetime(2026, 10, 20, tzinfo=UTC),
            model="gemini-3.5-flash-lite",
        ),
        make_record(
            "request-2",
            datetime(2026, 10, 22, tzinfo=UTC),
            model="gemini-3.5-flash",
        ),
    ]

    dataframe = records_to_dataframe(records)

    filtered = filter_history_dataframe(
        dataframe,
        start_date=date(2026, 10, 21),
        end_date=date(2026, 10, 22),
        model="gemini-3.5-flash",
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["model"] == "gemini-3.5-flash"


def test_daily_aggregations_use_actual_records() -> None:
    records = [
        make_record(
            "request-1",
            datetime(2026, 10, 20, 9, tzinfo=UTC),
        ),
        make_record(
            "request-2",
            datetime(2026, 10, 20, 10, tzinfo=UTC),
        ),
    ]

    dataframe = records_to_dataframe(records)

    activity = daily_request_activity(dataframe)
    emissions = daily_reference_emissions(dataframe)

    assert activity.iloc[0]["request_count"] == 2
    assert emissions.iloc[0]["reference_carbon_gco2e"] == 0.06


def test_analytics_ignore_records_with_invalid_timestamps() -> None:
    dataframe = records_to_dataframe(
        [
            make_record(
                "request-1",
                datetime(2026, 10, 20, 9, tzinfo=UTC),
            )
        ]
    )
    dataframe["timestamp"] = dataframe["timestamp"].astype("object")
    dataframe.loc[1] = dataframe.loc[0]
    dataframe.loc[1, "request_id"] = "request-invalid"
    dataframe.loc[1, "timestamp"] = "not-a-timestamp"

    filtered = filter_history_dataframe(dataframe)
    activity = daily_request_activity(dataframe)
    emissions = daily_reference_emissions(dataframe)

    assert filtered["request_id"].tolist() == ["request-1"]
    assert activity.iloc[0]["request_count"] == 1
    assert emissions.iloc[0]["reference_carbon_gco2e"] == 0.03
