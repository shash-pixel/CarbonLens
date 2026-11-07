"""Tests for the active-session Gemini result display."""

from datetime import UTC, datetime

from streamlit.testing.v1 import AppTest


def successful_result_showcase() -> None:
    """Render one successful tracked inference without calling Gemini."""
    from datetime import UTC, datetime
    
    from app import render_result
    from tracking.usage_tracker import TrackedInference

    record = TrackedInference(
        request_id="test-request-001",
        timestamp=datetime(2026, 11, 7, 10, 30, tzinfo=UTC),
        provider="google",
        model="gemini-3.5-flash-lite",
        status="success",
        latency_ms=725.0,
        input_tokens=8,
        output_tokens=12,
        total_tokens=20,
        reference_energy_wh=0.24,
        reference_carbon_gco2e=0.03,
        estimation_method=(
            "Google published median Gemini Apps text-prompt "
            "benchmark (May 2025 analysis)"
        ),
        estimation_classification="reference_benchmark",
        estimation_note=(
            "Published reference values, not direct measurements "
            "of this API request."
        ),
        response_text="A session-only Gemini response.",
    )

    render_result(record)


def test_result_display_shows_reference_values_without_errors() -> None:
    """A successful result must display benchmark values and metadata."""
    app = AppTest.from_function(successful_result_showcase).run()

    displayed_subheaders = [
        element.value
        for element in app.subheader
    ]

    assert not app.exception
    assert "Generated response" in displayed_subheaders
    assert "0.24 Wh" in displayed_subheaders
    assert "0.03 g CO₂e" in displayed_subheaders