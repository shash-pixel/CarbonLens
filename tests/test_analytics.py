from datetime import UTC, datetime

from analytics.analytics_service import history_summary
from tracking.usage_tracker import TrackedInference


def make_record(
    request_id: str,
    status: str,
    latency_ms: float | None = None,
    reference_carbon_gco2e: float | None = None,
    estimation_classification: str | None = None,
) -> TrackedInference:
    return TrackedInference(
        request_id=request_id,
        timestamp=datetime.now(UTC),
        provider="google",
        model="gemini-3.5-flash-lite",
        status=status,
        latency_ms=latency_ms,
        reference_carbon_gco2e=reference_carbon_gco2e,
        estimation_classification=estimation_classification,
    )


def test_history_summary_counts_only_reference_benchmark_records() -> None:
    records = [
        make_record(
            request_id="success-1",
            status="success",
            latency_ms=100,
            reference_carbon_gco2e=0.03,
            estimation_classification="reference_benchmark",
        ),
        make_record(
            request_id="success-2",
            status="success",
            latency_ms=200,
            reference_carbon_gco2e=0.03,
            estimation_classification="reference_benchmark",
        ),
        make_record(
            request_id="failure-1",
            status="failed",
        ),
    ]

    summary = history_summary(records)

    assert summary.total_requests == 3
    assert summary.successful_requests == 2
    assert summary.reference_benchmark_count == 2
    assert summary.published_reference_carbon_total_gco2e == 0.06
    assert summary.average_latency_ms == 150


def test_history_summary_keeps_missing_values_unavailable() -> None:
    records = [
        make_record(
            request_id="failure-1",
            status="failed",
        )
    ]

    summary = history_summary(records)

    assert summary.reference_benchmark_count == 0
    assert summary.published_reference_carbon_total_gco2e is None
    assert summary.average_latency_ms is None